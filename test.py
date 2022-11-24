from multiprocessing import Pool
from time import sleep
import os

list = "./CorrectImages/Keword/12.jpg"

print(list[:-4].replace("./CorrectImages/{}".format("Keword"), ""))