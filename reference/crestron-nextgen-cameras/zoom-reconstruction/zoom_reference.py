"""Doc-only reconstruction of the Crestron 1 Beyond NextGen camera zoom transformations.

Sources:
  Zoom ratio/position tables:
    https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm
  Optical zoom per model (which table applies):
    .../Specifications/I12Specs.htm, I20Specs.htm, P12Specs.htm, P20Specs.htm
  Digital zoom limit x1-x16:
    .../Configuration/On-Screen-Display(OSD)-Menu.htm
Declarative context: driver_definition of
  Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg / ..._P20_IP.pkg
"""

# --- Published tables (VISCA-Commands.htm, "Zoom Ratio / Position (CAM_Zoom)") -------
POS_12 = [0x0000, 0x1982, 0x24E2, 0x2BC9, 0x3099, 0x343D,
          0x3724, 0x3988, 0x3B8B, 0x3D43, 0x3EBB, 0x4000]
POS_20 = [0x0000, 0x1851, 0x22BE, 0x28F6, 0x2D45, 0x3086, 0x3320, 0x3549,
          0x371E, 0x38B3, 0x3A12, 0x3B42, 0x3C47, 0x3D25, 0x3DDF, 0x3E7B,
          0x3EFB, 0x3F64, 0x3FBA, 0x4000]
LEV_12 = [float(i) for i in range(1, 13)]
LEV_20 = [float(i) for i in range(1, 21)]

TABLES = {
    "IV-CAM-I12": (LEV_12, POS_12),
    "IV-CAM-P12": (LEV_12, POS_12),
    "IV-CAM-I20": (LEV_20, POS_20),
    "IV-CAM-P20": (LEV_20, POS_20),
}

POSITION_MIN_OPTICAL = 0
POSITION_MAX_OPTICAL = 0x4000      # 16384; matches driver Conditions ZoomPosition{Is,FromLevel} vs 16384


def zoom_level_to_position(level, model):
    """Piecewise-LINEAR interpolation of the published level->position table.

    Below the first row -> clamp to 0.  Above the last row -> linear extrapolation
    on the final segment, so the result exceeds 16384 and the driver's
    ZoomLevelIsGreaterThanOpticalZoomMax rule fires.  Result rounded to int
    (a 16-bit VISCA field).
    """
    levels, positions = TABLES[model]
    if level <= levels[0]:
        return positions[0]
    for i in range(len(levels) - 1):
        if level <= levels[i + 1]:
            f = (level - levels[i]) / (levels[i + 1] - levels[i])
            return int(round(positions[i] + f * (positions[i + 1] - positions[i])))
    # extrapolate past the tele end on the slope of the last segment
    f = (level - levels[-2]) / (levels[-1] - levels[-2])
    return int(round(positions[-2] + f * (positions[-1] - positions[-2])))


def zoom_position_to_level(position, model):
    """Inverse of the above over the OPTICAL range only (0..16384).

    Positions above 16384 are the camera's digital-zoom range (driver
    ZoomPosition.Max = 31424 = 0x7AC0).  The documentation publishes no
    position<->ratio mapping for that range, so this raises.
    """
    levels, positions = TABLES[model]
    if position <= positions[0]:
        return levels[0]
    if position > POSITION_MAX_OPTICAL:
        raise NotImplementedError(
            "digital-zoom range 16385..31424 is undocumented")
    for i in range(len(positions) - 1):
        if position <= positions[i + 1]:
            f = (position - positions[i]) / (positions[i + 1] - positions[i])
            return levels[i] + f * (levels[i + 1] - levels[i])
    return levels[-1]


def apply_zoom_position_step(position, model, mode):
    """NOT RECONSTRUCTIBLE from the documentation.

    The docs publish no zoom-position granularity for these lenses; the only
    step-like quantities documented are the 0-7 zoom SPEED parameter and the
    driver's own ZoomPosition.Step = 1 / ZoomLevel.Step = 0.1.
    """
    raise NotImplementedError("undetermined by documentation")


# --- VISCA framing, for the byte-level check ---------------------------------------
def visca_extract_nibbles(value):
    """Driver command SetZoomPosition emits '{Y4} {Y3} {Y2} {Y1}'."""
    y1 = value & 0xF
    y2 = (value >> 4) & 0xF
    y3 = (value >> 8) & 0xF
    y4 = (value >> 12) & 0xF
    return y1, y2, y3, y4


def set_zoom_position_packet(position, speed, visca_address=1):
    y1, y2, y3, y4 = visca_extract_nibbles(position)
    return bytes([0x80 + visca_address, 0x01, 0x04, 0x47,
                  speed & 0xFF, y4, y3, y2, y1, 0xFF])
