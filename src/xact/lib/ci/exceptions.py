# -*- coding: utf-8 -*-


# =============================================================================
class Nonconformity(Exception):
    """
    Thrown to report a nonconformity.

    """

    # -------------------------------------------------------------------------
    def __init__(self, tool, msg_id, msg, filepath, line, col):
        """
        Instantiate and return a new Nonconformity exception.

        """
        self.tool     = tool
        self.msg_id   = msg_id
        self.msg      = msg
        self.filepath = filepath
        self.line     = line
        self.col      = col

    # -------------------------------------------------------------------------
    def asdict(self):
        """
        Return nonconformity details as a dictionary,

        """
        return dict(tool     = self.tool,
                    msg_id   = self.msg_id,
                    msg      = self.msg,
                    filepath = self.filepath,
                    line     = self.line,
                    col      = self.col)
