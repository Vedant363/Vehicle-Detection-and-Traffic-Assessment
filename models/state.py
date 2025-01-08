class VideoState:
    _show_video = True

    @classmethod
    def get_show_video(cls):
        return cls._show_video

    @classmethod
    def set_show_video(cls, value):
        cls._show_video = value

class DecryptionStatus:
    _decryption_ok = False

    @classmethod
    def get_decryption_status(cls):
        """Get the decryption status"""
        return cls._decryption_ok

    @classmethod
    def set_decryption_status(cls, value):
        """Set the decryption status"""
        cls._decryption_ok = value

class StopExecution:
    _stop_execution = False

    @classmethod
    def get_stop_execution_status(cls):
        return cls._stop_execution
   
    @classmethod
    def set_stop_execution_status(cls, value):
        cls._stop_execution = value