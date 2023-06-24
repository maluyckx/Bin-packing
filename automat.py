import glob, os
os.chdir("/home/marco/Bureau/ULB/BA3/BA3Q2/algo3/intro/Instances/Instances/") # changer en mettant un path correct pour vous
for file in glob.glob("instance*"):
    print("########### " + file)
    os.system("python3 generate_model.py "+ file +" 0") # changer le "0" en le paramètre souhaité
    print("------------")
    print("------------")
    print("------------")
    print("------------")
