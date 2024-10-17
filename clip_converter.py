import os
import sys
import subprocess
import copy
from datetime import datetime, timedelta
import time

FFMPEG_PATH = r"C:\cmdtools\ffmpeg.exe"
CRF = "10"
BASE_COMMAND = [FFMPEG_PATH, "-ss", "{startTime}", "-i", "{file}", "-strict", "experimental", "-f", "mp4", "-map_chapters", "-1", "-map", "0:0", "-map", "0:1", "-sn", "-c:a:0", "aac", "-b:a:0", "192k", "-c:v:0", "libx264", "-crf", CRF, "-mbd:v:0", "rd", "-mbcmp:v:0", "rd", "-cmp:v:0", "rd", "-precmp:v:0", "rd", "-subcmp:v:0", "rd", "-trellis:v:0", "1", "-ss", "00:00:15.000", "-t", "{timeLength}", "-y", "{output}"]
TIME_FORMAT = "%H:%M:%S.%f"

class OutputFile():
    Name = ""
    StartTime = ""
    EndTime = ""

    def Print(self):
        print(self.GetPrint())

    def GetPrint(self):
        return "Name: \"{name}\"  -- {start} - {end}".format(name=self.Name, start=self.StartTime, end=self.EndTime)

class ImportDetails():
    ImportFile = ""
    OutputFolder = ""
    OutputFiles = []

    def Print(self):
        print("")
        print("printing")
        print(self.ImportFile)
        print(self.OutputFolder)
        for file in self.OutputFiles:
            file.Print()


def Main(importFile):
    details = ImportClipDetails(importFile)

    for file in details.OutputFiles:
        print("Encoding: {file}".format(file=file.GetPrint()))
        EncodeFile(details, file)

    return details

def ImportClipDetails(importFile):
    lines = []
    details = ImportDetails()
    with open(importFile, "r", encoding="utf-8") as f:
        lines = f.readlines()
    index = 0
    for line in lines:
        print(line)
        if (index == 0):
            details.ImportFile = line.strip()
            index = index + 1
        elif (index == 1):
            details.OutputFolder = line.strip()
            index = index + 1
        elif (line.strip() != ""):
            lineSplit = line.split(">")
            times = lineSplit[0]
            outputName = lineSplit[1]
            output = OutputFile()
            output.Name = outputName.strip()
            timeSplit = times.split("-")
            output.StartTime = timeSplit[0].strip()
            output.EndTime = timeSplit[1].strip()
            details.OutputFiles.append(output)
            index = index + 1
    return details

def EncodeFile(details, file):
    commands = copy.deepcopy(BASE_COMMAND)
    outputPath = os.path.join(details.OutputFolder, file.Name)
    for i in range(0, len(commands)):
        value = commands[i]
        if (value == "{startTime}"):
            commands[i] = GetStartTime(file.StartTime)
        elif (value == "{file}"):
            commands[i] = details.ImportFile
        elif (value == "{timeLength}"):
            commands[i] = GetDuration(file.StartTime, file.EndTime)
        elif (value == "{output}"):
            commands[i] = outputPath
    subprocess.call(commands)


def GetStartTime(time):
    timeObject = datetime.strptime(time, TIME_FORMAT)
    startTimeObject = timeObject - timedelta(seconds=15)
    startTime = startTimeObject.time().strftime(TIME_FORMAT)
    splitTime = startTime.split(".")
    if (len(splitTime[1]) > 3):
        startTime = startTime[:-(len(splitTime[1])-3)]
    return startTime

def GetDuration(start, end):
    startTime = datetime.strptime(start, TIME_FORMAT)
    endTime = datetime.strptime(end, TIME_FORMAT)
    durationObject = endTime - startTime
    durationTime = (datetime.min + durationObject).time()
    duration = durationTime.strftime(TIME_FORMAT)
    durationSplit = duration.split(".")
    if (len(durationSplit[1]) > 3):
        duration = duration[:-(len(durationSplit[1])-3)]
    return duration

if __name__ == "__main__":
    print(sys.argv)
    if (len(sys.argv) != 2):
        print("IDIOT")
        quit()
    Main(sys.argv[1])
