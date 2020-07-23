import time
import os

import youtube_dl

import cheesepi
from cheesepi.tasks.task import Task

LOGGER = cheesepi.config.get_logger(__name__)

class Dash(Task):

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "dash"
        if not 'source' in spec:
            self.spec['source'] = "http://www.youtube.com/watch?v=_OBlgSz8sSM"

    # actually perform the measurements, no arguments required
    def run(self):
        LOGGER.info("Dash download: %s @ %f, PID: %d", self.spec['source'], time.time(), os.getpid())
        self.measure()

    # measure and record funtion
    def measure(self):
        self.spec['start_time'] = cheesepi.utils.now()
        self.perform()
        self.spec['end_time'] = cheesepi.utils.now()
        #LOGGER.debug(op_output)
        if 'download_speed' not in self.spec:
            self.spec['download_speed'] = self.spec['downloaded'] / (self.spec['end_time']
                                                                     - self.spec['start_time'])
        self.dao.write_op(self.spec['taskname'], self.spec)

    def perform(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': LOGGER,
            'progress_hooks': [self.callback],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([self.spec['source']])
            except Exception as exception:
                LOGGER.error("Problem with Dash download: %s", str(exception))
                #self.spec['status'] = "error"

    def callback(self, stats):
        #LOGGER.info(stats)
        if stats['status'] == 'finished':
            if 'downloaded_bytes' in stats:
                self.spec['downloaded'] = stats['downloaded_bytes']
            else:
                self.spec['downloaded'] = stats['total_bytes']

            if 'elapsed' in stats:
                self.spec['download_speed'] = self.spec['downloaded'] / stats['elapsed']

            try:
                # avoid cluttering the filesystem
                os.remove(stats['filename'])
            except Exception as exception:
                LOGGER.error("Problem removing Dash.py Youtube file %s: %s",
                             stats['filename'], str(exception))


if __name__ == "__main__":
    #general logging here? unable to connect etc
    DAO = cheesepi.storage.get_dao()

    SPEC = {'source':'http://www.youtube.com/watch?v=_OBlgSz8sSM'}
    DASH_TASK = Dash(DAO, SPEC)
    DASH_TASK.run()
