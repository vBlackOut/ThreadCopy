import Queue, threading, os, time
import shutil

fileQueue = Queue.Queue()
destPath = 'path/to/cop'

class ThreadedCopy:
    totalFiles = 0
    copyCount = 0
    lock = threading.Lock()

    def __init__(self):
        with open("filelist.txt", "r") as txt: #txt with a file per line
            fileList = txt.read().splitlines()

        if not os.path.exists(destPath):
            os.mkdir(destPath)

        self.totalFiles = len(fileList)

        print str(self.totalFiles) + " files to copy."
        self.threadWorkerCopy(fileList)


    def CopyWorker(self):
        while True:
            fileName = fileQueue.get()
            shutil.copy(fileName, destPath)
            fileQueue.task_done()
            with self.lock:
                self.copyCount += 1
                percent = (self.copyCount * 100) / self.totalFiles
                print str(percent) + " percent copied."

    def threadWorkerCopy(self, fileNameList):
        for i in range(16):
            t = threading.Thread(target=self.CopyWorker)
            t.daemon = True
            t.start()
        for fileName in fileNameList:
            fileQueue.put(fileName)
        fileQueue.join()

ThreadedCopy()
