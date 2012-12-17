import os
names = os.listdir("/home/")
names = filter(lambda n: n[0] not in ['.', '_', '-'], names)
