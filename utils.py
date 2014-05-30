def tosgn(v):
    """
    Convert from MODBUS read-in value to signed 16bit
    """
    v = int(v)
    if v > 32767:
        return 32768 - v
    else:
        return v
    
def totmp(v):
    return tosgn(v) / 10