-- qsys_dm_md_ctp.lua
--
-- Q-SYS Lua reference driver for Crestron DM-MD8X8-CPU3-RPS (and compatible
-- CPU3/CPU4 DM-MD chassis) routing control via the chassis's CTP console on
-- TCP :41795.
--
-- Can be loaded into Q-SYS Designer as:
--   (a) A Script Component ("Text Controller" pointing at this .lua), OR
--   (b) The runtime of a packaged .qplug (plugin). The GetControls/GetPins
--       stubs at the bottom show the .qplug shape; the active runtime below
--       works equally well as a Script Component.
--
-- Verified protocol surface (from live chassis experiments; see evidence/01-15
-- in the extron-driver-convert research branch):
--   SETVIDEOROUTE inputSlotId outputSlotId   -- 0 input breaks the route
--   SETAUDIOROUTE inputSlotId outputSlotId
--   SETAVROUTE inputSlotId outputSlotId      -- A+V together
--   SETUSBROUTE inputSlotId outputSlotId
--   SETAVUROUTE inputSlotId outputSlotId     -- A+V+USB
--   SETAVALLROUTE inputSlotId                -- one input to ALL outputs
--   DUMPDMROUTEINFO [slotId]                 -- read route state
--   REPORTDM                                 -- read attached endpoint info
--
-- NOT supported through this driver: endpoint RS-232 / IR / Relay. Those are
-- firmware-locked on the chassis (see evidence/13 in the research branch);
-- SIMPL# Pro add-on or per-room-local control hardware is required for them.

-- ---------- Configuration (edit for your chassis) --------------------------

local HOST = "192.168.6.14"
local PORT = 41795
local INPUTS = 8                   -- DM-MD8X8-CPU3-RPS has 8 inputs
local OUTPUTS = 8                  -- and 8 outputs
local POLL_INTERVAL_SECONDS = 10   -- how often to poll DUMPDMROUTEINFO for status
local RECONNECT_BACKOFF_S = 5      -- socket reconnect delay on close/error

-- ---------- Controls (visible on the Q-SYS component surface) --------------

-- These names are the Q-SYS "control" names. In Script Component mode, access
-- them via Controls.<name>. In .qplug mode, declare them in GetControls().

-- Expected controls:
--   VideoInput[1..OUTPUTS]  -- integer, 1..INPUTS, 0 = disconnected
--   AudioInput[1..OUTPUTS]
--   USBInput[1..OUTPUTS]
--   SelectAllInput          -- integer 1..INPUTS; writing it sends SETAVALLROUTE
--   PollNow                 -- trigger: force an immediate DUMPDMROUTEINFO
--   Connected               -- bool indicator
--   LastResponse            -- string status
--   LastError               -- string, last protocol error

-- ---------- TCP transport --------------------------------------------------

local socket = TcpSocket.New()
socket.ReadTimeout = 2
socket.WriteTimeout = 2
socket.ReconnectTimeout = RECONNECT_BACKOFF_S

local rxbuf = ""
local pending_response_callback = nil

local function log(fmt, ...) print(string.format("[dm-ctp] " .. fmt, ...)) end

local function send_line(cmd, on_response)
  if not socket.IsConnected then
    log("send skipped (not connected): %s", cmd)
    return false
  end
  pending_response_callback = on_response
  socket:Write(cmd .. "\r\n")
  log("TX: %s", cmd)
  return true
end

-- ---------- Command surface ------------------------------------------------

local function route_video(input, output)
  assert(0 <= input and input <= INPUTS, "video input out of range")
  assert(1 <= output and output <= OUTPUTS, "video output out of range")
  -- Chassis internal slot IDs: inputs 1..N, outputs 101..108
  return send_line(string.format("SETVIDEOROUTE %d %d", input, 100 + output))
end

local function route_audio(input, output)
  assert(0 <= input and input <= INPUTS)
  assert(1 <= output and output <= OUTPUTS)
  return send_line(string.format("SETAUDIOROUTE %d %d", input, 100 + output))
end

local function route_av(input, output)
  assert(0 <= input and input <= INPUTS)
  assert(1 <= output and output <= OUTPUTS)
  return send_line(string.format("SETAVROUTE %d %d", input, 100 + output))
end

local function route_usb(input, output)
  assert(0 <= input and input <= INPUTS)
  assert(1 <= output and output <= OUTPUTS)
  return send_line(string.format("SETUSBROUTE %d %d", input, 100 + output))
end

local function route_all(input)
  assert(0 <= input and input <= INPUTS)
  return send_line(string.format("SETAVALLROUTE %d", input))
end

local function break_output(output)
  return route_av(0, output)
end

local function poll_routes()
  return send_line("DUMPDMROUTEINFO", on_dumpdmrouteinfo_response)
end

-- ---------- Response parsing ----------------------------------------------

-- DUMPDMROUTEINFO output format (observed from live chassis):
-- --------------------------------------------------------------------------
-- DM Routing Information for all Output cards
--  Routing Information for Input Card at Slot 1
-- No USB connection
--  Routing Information for Output Card at Slot 101
-- Video from Input Card at Slot 1
-- Audio from Input Card at Slot 1
-- USB from Input Card at Slot 1
-- Hot plug is Low  / Hot plug is High
-- ...
-- --------------------------------------------------------------------------

local function parse_dumpdmrouteinfo(text)
  local routes = { video = {}, audio = {}, usb = {} }
  local current_output = nil
  for line in text:gmatch("[^\r\n]+") do
    local out_slot = line:match("Routing Information for Output Card at Slot (%d+)")
    if out_slot then
      current_output = tonumber(out_slot) - 100  -- 101 -> output 1
    elseif current_output then
      if line:match("No Video connection") then
        routes.video[current_output] = 0
      else
        local in_slot = line:match("Video from Input Card at Slot (%d+)")
        if in_slot then routes.video[current_output] = tonumber(in_slot) end
      end
      if line:match("No Audio connection") then
        routes.audio[current_output] = 0
      else
        local in_slot = line:match("Audio from Input Card at Slot (%d+)")
        if in_slot then routes.audio[current_output] = tonumber(in_slot) end
      end
      if line:match("No USB connection") then
        routes.usb[current_output] = 0
      else
        local in_slot = line:match("USB from Input Card at Slot (%d+)")
        if in_slot then routes.usb[current_output] = tonumber(in_slot) end
      end
    end
  end
  return routes
end

function on_dumpdmrouteinfo_response(text)
  local routes = parse_dumpdmrouteinfo(text)
  for out = 1, OUTPUTS do
    if routes.video[out] ~= nil then Controls["VideoInput"][out].Value = routes.video[out] end
    if routes.audio[out] ~= nil then Controls["AudioInput"][out].Value = routes.audio[out] end
    if routes.usb[out] ~= nil   then Controls["USBInput"][out].Value   = routes.usb[out]   end
  end
  Controls["LastResponse"].String = "poll ok"
end

-- ---------- Wire the socket events ----------------------------------------

socket.Connected = function(sock)
  log("connected to %s:%d", HOST, PORT)
  if Controls["Connected"] then Controls["Connected"].Boolean = true end
  rxbuf = ""
  poll_routes()
end

socket.Reconnect = function(sock)
  log("reconnecting...")
  if Controls["Connected"] then Controls["Connected"].Boolean = false end
end

socket.Error = function(sock, err)
  log("socket error: %s", tostring(err))
  if Controls["LastError"] then Controls["LastError"].String = tostring(err) end
  if Controls["Connected"] then Controls["Connected"].Boolean = false end
end

socket.Closed = function(sock)
  log("socket closed; will reconnect in %ds", RECONNECT_BACKOFF_S)
  if Controls["Connected"] then Controls["Connected"].Boolean = false end
end

socket.Data = function(sock)
  local chunk = sock:ReadLine(TcpSocket.EReadMode.NoCRLF, 65536)
  while chunk ~= nil do
    rxbuf = rxbuf .. chunk .. "\n"
    chunk = sock:ReadLine(TcpSocket.EReadMode.NoCRLF, 65536)
  end
  -- Prompt-based response boundary: console returns ">" or similar at end.
  -- Simpler heuristic: if we have pending callback and buffer is non-empty +
  -- quiet for a short time, call it. We approximate "quiet" by draining
  -- everything available each Data event and consuming the buffer when the
  -- idle timer fires.
  if pending_response_callback and rxbuf:find("\n") then
    local text = rxbuf
    rxbuf = ""
    local cb = pending_response_callback
    pending_response_callback = nil
    local ok, err = pcall(cb, text)
    if not ok then
      log("response handler error: %s", tostring(err))
      if Controls["LastError"] then Controls["LastError"].String = tostring(err) end
    end
  end
end

-- ---------- Control wiring (writes from the Q-SYS UI) ---------------------

for out = 1, OUTPUTS do
  if Controls["VideoInput"] and Controls["VideoInput"][out] then
    Controls["VideoInput"][out].EventHandler = function(ctl)
      route_video(math.floor(ctl.Value + 0.5), out)
    end
  end
  if Controls["AudioInput"] and Controls["AudioInput"][out] then
    Controls["AudioInput"][out].EventHandler = function(ctl)
      route_audio(math.floor(ctl.Value + 0.5), out)
    end
  end
  if Controls["USBInput"] and Controls["USBInput"][out] then
    Controls["USBInput"][out].EventHandler = function(ctl)
      route_usb(math.floor(ctl.Value + 0.5), out)
    end
  end
end

if Controls["SelectAllInput"] then
  Controls["SelectAllInput"].EventHandler = function(ctl)
    route_all(math.floor(ctl.Value + 0.5))
  end
end

if Controls["PollNow"] then
  Controls["PollNow"].EventHandler = function(ctl)
    if ctl.Boolean then poll_routes() end
  end
end

-- ---------- Periodic status poll ------------------------------------------

local poll_timer = Timer.New()
poll_timer.EventHandler = function() poll_routes() end
poll_timer:Start(POLL_INTERVAL_SECONDS)

-- ---------- Open the connection ------------------------------------------

socket:Connect(HOST, PORT)
log("boot: connecting to %s:%d", HOST, PORT)


-- =========================================================================
-- Below: skeleton for packaging this as a .qplug plugin (optional).
-- When used as a Script Component (recommended for a one-off installation),
-- these functions are ignored.
-- =========================================================================

--[[
PluginInfo = {
  Name = "Crestron~DM-MD CPU3 Routing (CTP)",
  Version = "1.0.0",
  Id = "crestron-dm-md-ctp-routing-01",
  Description = "Routing-only driver for Crestron DM-MD CPU3/CPU4 chassis via CTP :41795. "
             .. "Endpoint I/O is NOT supported (firmware-locked). See evidence/13.",
  ShowDebug = true,
}

function GetProperties()
  return {
    { Name = "IP Host",   Type = "string", Value = "192.168.6.14" },
    { Name = "Inputs",    Type = "integer", Value = 8, Min = 1, Max = 32 },
    { Name = "Outputs",   Type = "integer", Value = 8, Min = 1, Max = 32 },
  }
end

function GetControls(props)
  local ctrls = {}
  for i = 1, props["Outputs"].Value do
    table.insert(ctrls, { Name = "VideoInput[" .. i .. "]", ControlType = "Knob", ControlUnit = "Integer", Min = 0, Max = props["Inputs"].Value })
    table.insert(ctrls, { Name = "AudioInput[" .. i .. "]", ControlType = "Knob", ControlUnit = "Integer", Min = 0, Max = props["Inputs"].Value })
    table.insert(ctrls, { Name = "USBInput["   .. i .. "]", ControlType = "Knob", ControlUnit = "Integer", Min = 0, Max = props["Inputs"].Value })
  end
  table.insert(ctrls, { Name = "SelectAllInput", ControlType = "Knob", ControlUnit = "Integer", Min = 0, Max = props["Inputs"].Value })
  table.insert(ctrls, { Name = "PollNow", ControlType = "Button", ButtonType = "Trigger" })
  table.insert(ctrls, { Name = "Connected", ControlType = "Indicator", IndicatorType = "LED" })
  table.insert(ctrls, { Name = "LastResponse", ControlType = "Indicator", IndicatorType = "Text" })
  table.insert(ctrls, { Name = "LastError",    ControlType = "Indicator", IndicatorType = "Text" })
  return ctrls
end
--]]
