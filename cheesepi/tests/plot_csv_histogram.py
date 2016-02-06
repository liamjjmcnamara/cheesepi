import math
import numpy as np
import matplotlib.pyplot as plt

data = []

def parse_ping_csv(filename):
    data = np.genfromtxt(filename, delimiter=',', skip_header=1, skip_footer=3)
    # Remove any NaN occurence
    data = data[~np.isnan(data)]
    return data

def histplot(data, xmin=0, xmax=1000, step=1):

    y, x = np.histogram(data, bins=np.linspace(xmin, xmax, (xmax-xmin)/step),
            density=True)

    plt.bar(x[:-1], y, width=x[1]-x[0], color='red', alpha=0.5)
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="The csv file to parse")
    parser.add_argument("--max", type=int, default=1000,
            help="The upper limit of the plot range")
    parser.add_argument("--min", type=int, default=0,
            help="The lower limit of the plot range")
    parser.add_argument("--step", type=float, default=1,
            help="The step size of the buckets")

    args = parser.parse_args()

    if args.file is None:
        print("No file given...")
    else:
        data = parse_ping_csv(args.file)
        histplot(data, xmin=args.min, xmax=args.max, step=args.step)
