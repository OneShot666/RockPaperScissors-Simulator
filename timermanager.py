class TimerManager:                                                             # To manage all timers in program
    def __init__(self, duration=0, min_duration: int | float = None, max_duration: int | float = None):
        self.is_paused_flag = True                                              # Pause by default
        self.duration = None                                                    # In second
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.nb_loop = 0
        self.start_time: float = None
        self.pause_time: float = None
        self.total_pause_duration = 0
        self.set_duration(duration)

    def set_duration(self, new_duration: int | float):                          # Change duration of loop (can't exceed limits)
        if self.min_duration:
            new_duration = max(self.min_duration, new_duration)
        if self.max_duration:
            new_duration = min(self.max_duration, new_duration)
        self.duration = new_duration
        if self.duration > 0 and self.nb_loop == 0:
            self.nb_loop = 1

    def increase_duration(self):                                                # Increase duration by one (not under limit)
        self.duration += 1
        if self.max_duration is not None:
            self.duration = min(self.max_duration, self.duration)

    def reduce_duration(self):                                                  # Reduce duration by one (not under limit)
        self.duration -= 1
        if self.min_duration is not None:
            self.duration = max(self.min_duration, self.duration)

    def get_elapsed_time(self, current_time: float):                            # Return time since timer start (in sec)
        if self.start_time is not None:
            result = (self.pause_time if self.is_paused_flag else current_time) - self.start_time - self.total_pause_duration
            return round(result, 1)
        return -1

    def get_total_pause_duration(self):                                         # Return total time of pause
        return self.total_pause_duration

    def get_paused(self):                                                       # Return if timer is paused
        return self.is_paused_flag

    def start(self, current_time: float):                                       # (re)start timer
        self.is_paused_flag = False
        self.nb_loop = 0
        self.start_time = current_time
        self.pause_time = None
        self.total_pause_duration = 0

    def reset(self, current_time: float):                                       # Restart loop (doesn't reset nb of loop)
        self.is_paused_flag = False
        self.start_time = current_time
        self.pause_time = None
        self.total_pause_duration = 0

    def pause(self, current_time: float):                                       # Pause timer
        if not self.is_paused_flag:
            self.is_paused_flag = True
            self.pause_time = current_time

    def unpause(self, current_time: float):                                     # Unpause timer
        if self.is_paused_flag:
            self.is_paused_flag = False
            self.total_pause_duration += current_time - self.pause_time
            self.pause_time = None

    def check_loop_end(self, current_time: float):                              # Reset loop if duration is reached
        if not self.is_paused_flag and self.duration and self.start_time:       # If timer has been started and has loop
            if self.get_elapsed_time(current_time) >= self.duration:
                self.reset(current_time)
                self.nb_loop += 1
                return 1
            return -1
        return 0
