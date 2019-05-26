import queue, threading, os, time
import fnmatch
from collections import Counter
import argparse
import shutil


parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('src', help='source file or directory')
parser.add_argument('dest', help='destination file or directory')
args = parser.parse_args()

srcPath = args.src
destPath = args.dest

fileQueue = queue.Queue()

class ThreadedCopy:
    totalFiles = 0
    copyCount = 0
    lock = threading.Lock()

    def __init__(self, srcPath, destPath):
        self.srcPath = srcPath
        self.destPath = destPath

        allFiles = self.findFiles(self.srcPath)
        if not os.path.exists(self.destPath):
            os.mkdir(self.destPath)

        self.totalFiles = len(allFiles)

        print("{} files to copy.".format(self.totalFiles))
        self.threadWorkerCopy(allFiles)


    def findFiles(self, directory, pattern='*'):
        if not os.path.exists(directory):
            raise ValueError("Directory not found {}".format(directory))

        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if fnmatch.filter([full_path], pattern):
                    matches.append(os.path.join(root, filename))
        return matches

    def CopyWorker(self):
        while True:
            fileName = fileQueue.get()

            #if not os.path.exists(os.path.dirname(destPath)):
            #print(destPath+fileName)
            destPathClear = self.pathClean(destPath+fileName, destPath)
            #print(destPathClear)
            try:
                os.makedirs(os.path.dirname(destPathClear))
            except FileExistsError:
                pass
            try:
                shutil.copy(fileName, os.path.dirname(destPathClear))
            except PermissionError as e:
                print(e)
            fileQueue.task_done()
            with self.lock:
                self.copyCount += 1
                percent = (self.copyCount * 100) / self.totalFiles
                print("\033[F{} percent copied.".format(percent))

    def pathClean(self, stringPath, destPath):
        workPath = []

        for string in stringPath.split("/"):
            if string not in workPath:
             workPath.append(string)

        for string in destPath.split("/"):
            if string in workPath:
                workPath.remove(string)

        outFile = "{}/{}".format(self.destPath, "/".join(workPath[1:]))
        return outFile

    def threadWorkerCopy(self, fileNameList):
        for i in range(16):
            t = threading.Thread(target=self.CopyWorker)
            t.daemon = True
            t.start()
        for fileName in fileNameList:
            fileQueue.put(fileName)
        fileQueue.join()

ThreadedCopy(srcPath, destPath)
