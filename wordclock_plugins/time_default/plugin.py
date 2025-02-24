import datetime
import logging
import os
import time
import time_english
import time_french
import time_german
import time_german2
import time_swabian
import time_swabian2
import time_dutch
import time_bavarian
import time_swiss_german
import time_swiss_german2
import wordclock_tools.wordclock_colors as wcc


class plugin:
    """
    A class to display the current time (default mode).
    This default mode needs to be adapted to the hardware
    layout of the wordclock (the chosen stencil) and is
    the most essential time display mode of the wordclock.
    """

    def __init__(self, config):
        """
        Initializations for the startup of the current wordclock plugin
        """
        # Get plugin name (according to the folder, it is contained in)
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = "The time"
        self.description = "The minimum, you should expect from a wordclock."

        # For backward compatibility
        try:
            typewriter = config.getboolean('plugin_' + self.name, 'typewriter')
        except:
            typewriter = False

        # animation
        if typewriter:
            self.animation = "typewriter"
        else:
            try:
                self.animation = ''.join(config.get('plugin_' + self.name, 'animation'))
            except:
                self.animation = "fadeOutIn"

        animations = ["fadeOutIn", "typewriter", "none"]

        if self.animation not in animations:
            logging.warning('No animation set for default plugin within the config-file. ' + animations[0] + ' animation will be used.')
            self.animation = animations[0]

        try:
            self.animation_speed = config.getint('plugin_' + self.name, 'animation_speed')
        except:
            self.animation_speed = 5
            logging.warning('No animation_speed set for default plugin within the config-file. Defaulting to ' + str(
                self.animation_speed) + '.')

        try:
            self.purist = config.getboolean('plugin_time_default', 'purist')
        except:
            logging.warning('No purist-flag set for default plugin within the config-file. Prefix will be displayed.')
            self.purist = False

        # sleep mode
        try:
            self.sleep_begin = datetime.time(config.getint('plugin_' + self.name, 'sleep_begin_hour'),config.getint('plugin_' + self.name, 'sleep_begin_minute'),0)
        except:
            self.sleep_begin = datetime.time(0,0,0)
            self.sleep_end = datetime.time(0,0,0)
            logging.warning('  No sleeping time set, display will stay bright 24/7.')

        try:
            self.sleep_end = datetime.time(config.getint('plugin_' + self.name, 'sleep_end_hour'),config.getint('plugin_' + self.name, 'sleep_end_minute'),0)
        except:
            self.sleep_begin = datetime.time(0,0,0)
            self.sleep_end = datetime.time(0,0,0)
            logging.warning('  No sleeping time set, display will stay bright 24/7.')

        try:
            self.sleep_brightness = config.getint('plugin_' + self.name, 'sleep_brightness')
        except:
            self.sleep_brightness = 5
            logging.warning('  No sleep brightness set within the config-file. Defaulting to ' + str(
                self.sleep_brightness) + '.')
        
        # if left/right button is pressed during sleep cycle, the current sleep cycle is skipped for the rest of the night
        # to allow manual override
        self.skip_sleep = False
        self.is_sleep = False

        # monitor sleep mode changes to apply brightness
        self.sleep_switch = False

        # Choose default fgcolor
        try:
            fgcolor = ''.join(config.get('wordclock', 'default-fg-color'))
        except:
            # For backward compatibility
            fgcolor = ''.join(config.get('plugin_time_default', 'default-fg-color'))

        if fgcolor == 'BLACK':
            self.word_color = wcc.BLACK
            self.minute_color = wcc.BLACK
        elif fgcolor == 'WHITE':
            self.word_color = wcc.WHITE
            self.minute_color = wcc.WHITE
        elif fgcolor == 'WWHITE':
            self.word_color = wcc.WWHITE
            self.minute_color = wcc.WWHITE
        elif fgcolor == 'RED':
            self.word_color = wcc.RED
            self.minute_color = wcc.RED
        elif fgcolor == 'YELLOW':
            self.word_color = wcc.YELLOW
            self.minute_color = wcc.YELLOW
        elif fgcolor == 'LIME':
            self.word_color = wcc.LIME
            self.minute_color = wcc.LIME
        elif fgcolor == 'GREEN':
            self.word_color = wcc.GREEN
            self.minute_color = wcc.GREEN
        elif fgcolor == 'BLUE':
            self.word_color = wcc.BLUE
            self.minute_color = wcc.BLUE
        else:
            print('Could not detect default-fg-color: ' + fgcolor + '.')
            print('Choosing default: warm white')
            self.word_color = wcc.WWHITE
            self.minute_color = wcc.WWHITE

        # Choose default bgcolor
        try:
            bgcolor = ''.join(config.get('wordclock', 'default-bg-color'))
        except:
            # For backward compatibility
            bgcolor = ''.join(config.get('plugin_time_default', 'default-bg-color'))

        if bgcolor == 'BLACK':
            self.bg_color = wcc.BLACK
        elif bgcolor == 'WHITE':
            self.bg_color = wcc.WHITE
        elif bgcolor == 'WWHITE':
            self.bg_color = wcc.WWHITE
        elif bgcolor == 'RED':
            self.bg_color = wcc.RED
        elif bgcolor == 'YELLOW':
            self.bg_color = wcc.YELLOW
        elif bgcolor == 'LIME':
            self.bg_color = wcc.LIME
        elif bgcolor == 'GREEN':
            self.bg_color = wcc.GREEN
        elif bgcolor == 'BLUE':
            self.bg_color = wcc.BLUE
        else:
            print('Could not detect default-bg-color: ' + bgcolor + '.')
            print('Choosing default: black')
            self.bg_color = wcc.BLACK

        # Other color modes...
        self.color_modes = \
            [[wcc.BLACK, wcc.WWHITE, wcc.WWHITE],
             [wcc.BLACK, wcc.WHITE, wcc.WHITE],
             [wcc.BLACK, wcc.ORANGE, wcc.ORANGE],
             [wcc.BLACK, wcc.ORANGE, wcc.WWHITE],
             [wcc.BLACK, wcc.PINK, wcc.GREEN],
             [wcc.BLACK, wcc.RED, wcc.YELLOW],
             [wcc.BLACK, wcc.BLUE, wcc.RED],
             [wcc.BLACK, wcc.RED, wcc.BLUE],
             [wcc.YELLOW, wcc.RED, wcc.BLUE],
             [wcc.RED, wcc.BLUE, wcc.BLUE],
             [wcc.RED, wcc.WHITE, wcc.WHITE],
             [wcc.GREEN, wcc.YELLOW, wcc.PINK],
             [wcc.WWHITE, wcc.BLACK, wcc.BLACK],
             [wcc.BLACK, wcc.Color(30, 30, 30), wcc.Color(30, 30, 30)]]
        self.color_mode_pos = 0
        self.rb_pos = 0  # index position for "rainbow"-mode
        try:
            self.brightness_mode_pos = config.getint('wordclock_display', 'brightness')
        except:
            logging.warning("Brightness value not set in config-file: To do so, add a \"brightness\" between 1..255 to the [wordclock_display]-section.")
            self.brightness_mode_pos = 255
        self.brightness_change = 8

        # save current brightness for switching back from sleep mode
        self.wake_brightness = self.brightness_mode_pos

    def run(self, wcd, wci):
        """
        Displays time until aborted by user interaction on pin button_return
        """
        # Some initializations of the "previous" minute
        prev_min = -1

        while True:
            # Get current time
            now = datetime.datetime.now()
            # Check if this is the predefined sleep time (muted brightness) as defined in wordclock_config.cfg
            nowtime = datetime.time(now.hour,now.minute,0)
            if not (self.sleep_begin == self.sleep_end):
                if ((self.sleep_begin <= nowtime) and ((nowtime <= self.sleep_end) or (nowtime <= datetime.time(23,59,59))) or (datetime.time(0,0,0) <= nowtime <= self.sleep_end)):  # skip if color/brightness change has been done during the current sleep cycle
                    if not self.skip_sleep: 
                        self.brightness_mode_pos = self.sleep_brightness
                        self.sleep_switch = True  # brightness has been changed
                    self.is_sleep = True 
                else:
                    self.brightness_mode_pos = self.wake_brightness
                    self.sleep_switch = True  # brightness has been changed
                    self.skip_sleep = False   # reset skip flag, returning to normal sleep/wake cycle
                    self.is_sleep = False
            # has brightness changed? then implement change in wcd
            if self.sleep_switch:
                wcd.setBrightness(self.brightness_mode_pos)
                self.sleep_switch = False  # reset switch
            # Check, if a minute has passed (to render the new time)
            if prev_min < now.minute:
                # Set background color
                self.show_time(wcd, wci, animation=self.animation, animation_speed=self.animation_speed)
                prev_min = -1 if now.minute == 59 else now.minute
            event = wci.waitForEvent(2)
            # Switch display color, if button_left is pressed
            if event == wci.EVENT_BUTTON_LEFT:
                if self.is_sleep:    # if button is pressed during sleep cycle, allow override until next sleep cycle
                    self.skip_sleep = True 
                self.color_mode_pos += 1
                if self.color_mode_pos == len(self.color_modes):
                    self.color_mode_pos = 0
                self.bg_color = self.color_modes[self.color_mode_pos][0]
                self.word_color = self.color_modes[self.color_mode_pos][1]
                self.minute_color = self.color_modes[self.color_mode_pos][2]
                self.show_time(wcd, wci, animation=self.animation, animation_speed=self.animation_speed)
                time.sleep(0.2)
            if (event == wci.EVENT_BUTTON_RETURN) \
                    or (event == wci.EVENT_EXIT_PLUGIN) \
                    or (event == wci.EVENT_NEXT_PLUGIN_REQUESTED):
                return
            if event == wci.EVENT_BUTTON_RIGHT:
                if self.is_sleep:    # if button is pressed during sleep cycle, allow override until next sleep cycle
                    self.skip_sleep = True
                time.sleep(wci.lock_time)
                self.color_selection(wcd, wci)

    def show_time(self, wcd, wci, animation=None, animation_speed=25):
        now = datetime.datetime.now()
        # Set background color
        wcd.setColorToAll(self.bg_color, includeMinutes=True)
        # Returns indices, which represent the current time, when being illuminated
        taw_indices = wcd.taw.get_time(now, self.purist)
        wcd.setColorBy1DCoordinates(taw_indices, self.word_color)
        wcd.setMinutes(now, self.minute_color)
        wcd.show(animation, animation_speed)

    def color_selection(self, wcd, wci):
        while True:
            # BEGIN: Rainbow generation as done in rpi_ws281x strandtest example! Thanks to Tony DiCola for providing :)
            if self.rb_pos < 85:
                self.word_color = self.minute_color = wcc.Color(3 * self.rb_pos, 255 - 3 * self.rb_pos, 0)
            elif self.rb_pos < 170:
                self.word_color = self.minute_color = wcc.Color(255 - 3 * (self.rb_pos - 85), 0, 3 * (self.rb_pos - 85))
            else:
                self.word_color = self.minute_color = wcc.Color(0, 3 * (self.rb_pos - 170),
                                                                255 - 3 * (self.rb_pos - 170))
            # END: Rainbow generation as done in rpi_ws281x strandtest example! Thanks to Tony DiCola for providing :)
            # TODO: Evaluate taw_indices only every n-th loop (saving resources)
            now = datetime.datetime.now()  # Set current time
            taw_indices = wcd.taw.get_time(now, self.purist)
            wcd.setColorToAll(self.bg_color, includeMinutes=True)
            wcd.setColorBy1DCoordinates(taw_indices, self.word_color)
            wcd.setMinutes(now, self.minute_color)
            wcd.show()
            self.rb_pos += 1
            if self.rb_pos == 256: self.rb_pos = 0
            event = wci.waitForEvent(0.1)
            if event != wci.EVENT_INVALID:
                time.sleep(wci.lock_time)
                break
        while True:
            self.brightness_mode_pos += self.brightness_change
            # TODO: Evaluate taw_indices only every n-th loop (saving resources)
            now = datetime.datetime.now()  # Set current time
            taw_indices = wcd.taw.get_time(now, self.purist)
            wcd.setColorToAll(self.bg_color, includeMinutes=True)
            wcd.setColorBy1DCoordinates(taw_indices, self.word_color)
            wcd.setMinutes(now, self.minute_color)
            wcd.setBrightness(self.brightness_mode_pos)
            wcd.show()
            if self.brightness_mode_pos < abs(self.brightness_change) or self.brightness_mode_pos > 255 - abs(
                    self.brightness_change):
                self.brightness_change *= -1
            event = wci.waitForEvent(0.1)
            if event != wci.EVENT_INVALID:
                time.sleep(wci.lock_time)
                return
