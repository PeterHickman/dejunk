import os


def resize(source, destination, pixels):
    s1 = "{}x{}".format(pixels, pixels)
    s2 = "{}x{}".format(pixels * 2, pixels * 2)

    print("Resizing to create {} at {}".format(destination, s1))
    cmd = "convert -define jpeg:size={} -auto-orient {}'[0]' -thumbnail '{}>' -background transparent -gravity center -extent {} {}".format(s2, source, s1, s1, destination)

    os.system(cmd)
