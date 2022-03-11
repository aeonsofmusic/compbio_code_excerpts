#! /usr/bin/env python3

import argparse
from numpy import array
from numpy import transpose


def readArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inpath",
        nargs="*",
        type=str,
        required=True,
        help="The directory containing the file(s) you would like to execute through MrBayes. Must contain NEXUS files.",
    )
    parser.add_argument(
        "--nst",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments: 1, 2, 6, mixed. The substitution model of choice. The numbers 1, 2, and 6 represent the numbers of substitution types in different models. To jump between different models, you can set nst=mixed. Examples of models you can set with nst=6 are GTR and SYM; with nst=2 HKY and K2P, with nst=1 F81 and JC. Note that other parameters must be set along with nst in order to use a specific model.",
    )
    parser.add_argument(
        "--rates",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments: equal, gamma, lnorm, propinv, invgamma, adgamma, kmixture. This chooses the distribution of rates across all sites.",
    )
    parser.add_argument(
        "--ngammacat",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments: Positive integers. The number of discrete categories used to approximate the Gamma distribution. In most cases, 4 categories is enough, although increasing the number of categories can make analysis more accurate.",
    )
    parser.add_argument(
        "--brlenspr",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments:\nunconstrained:uniform(<num>,<num>)\nunconstrained:exponential(<number>)\nunconstrained:twoexp(<num>,<num>)\nunconstrained:gammadir(<num>,<num>,<num>,<num>)\nunconstrained:invgamdir(<num>,<num>,<num>,<num>)\nclock:uniform\nclock:birthdeath\nclock:coalescence\nclock:fossilization\nclock:speciestree\nfixed(<treename>)\nThis specifies the branch length prior.",
    )
    parser.add_argument(
        "--shapepr",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments:\nuniform(<number>,<number>)\nexponential(<number>)\nfixed(<number>)\nThis specifies the hyperprior for the gamma or log-normal shape parameter, the latter two distributions used as priors for among-site rate variation.",
    )
    parser.add_argument(
        "--statefreqpr",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments:\ndirichlet(<number>)\ndirichlet(<number>,...,<number>)\nfixed(equal)\nfixed(empirical)\nfixed(<number>,...,<number>)\nThis specifies the prior on the state frequencies of the GTR model.",
    )
    parser.add_argument(
        "--revmatpr",
        nargs="+",
        type=str,
        required=True,
        help="Available arguments:\ndirichlet(<number>,<number>,...,<number>)\nfixed(<number>,<number>,...,<number>)\nThis specifies the prior for the substitution rates of the GTR model for nucleotide data. A typical uninformative prior would be dirichlet(1,1,1,1,1,1) for each possible substitution rate in the GTR model.",
    )
    parser.add_argument(
        "--ngen",
        nargs="+",
        type=str,
        required=True,
        help="The number of generations run by MCMC. Positive integers only.",
    )
    parser.add_argument(
        "--samplefreq",
        nargs="+",
        type=str,
        required=True,
        help="This determines how often the MCMC is sampled. Positive integers only. For instance, setting this to 1000 will sample the chain every 1000 generations.",
    )
    parser.add_argument(
        "--printfreq",
        nargs="+",
        type=str,
        required=True,
        help="This determines how often information about the MCMC is printed onto the terminal. Positive integers only. For instance, setting this to 1000 will print information every 1000 generations.",
    )
    parser.add_argument(
        "--burninfrac",
        nargs="+",
        type=str,
        required=True,
        help="The fraction of samples that will be ignored in the final calculations. Numbers between 0 and 1 only. Setting this to 0.1 means 10% of the samples will be discarded.",
    )
    parser.add_argument(
        "--nchains",
        nargs="+",
        type=str,
        required=True,
        default="4",
        help="The number of chains run for each analysis. Positive integers only. The default is 4 chains: 1 cold and 3 heated.",
    )
    parser.add_argument(
        "--nruns",
        nargs="+",
        type=str,
        required=True,
        help="The number of simultaneous and independent MCMC runs. Positive integers only.",
    )
    parser.add_argument(
        "--outfile",
        type=str,
        required=True,
        help="The name of the NEXUS file containing the MrBayes blocks. The .nexus extension will be added by the code, so there is no need to add it manually to the name.",
    )
    parser.add_argument(
        "--autoclose",
        nargs="+",
        type=str,
        required=False,
        default="no",
        help="Setting this to yes will cause MrBayes to not ask you to continue the analysis. Default = no",
    )
    parser.add_argument(
        "--nowarnings",
        nargs="+",
        type=str,
        required=False,
        default="no",
        help="Setting this to yes will make MrBayes not give warnings about the analysis. Default = no",
    )
    parser.add_argument(
        "--seed",
        nargs="+",
        type=int,
        required=False,
        help="Sets seed(s) for the random number generator. For fully reproducible results, use this option.",
    )
    args = parser.parse_args()
    return args


# Takes in command line arguments and formats them into a MrBayes block
def paraminputs(outfile, args):
    outfile.write(
        "\tlset nst="
        + str(args.nst)
        + " rates="
        + str(args.rates)
        + " ngammacat="
        + str(args.ngammacat)
        + ";\n"
    )
    outfile.write(
        "\tprset brlenspr="
        + str(args.brlenspr)
        + " shapepr="
        + str(args.shapepr)
        + " statefreqpr="
        + str(args.statefreqpr)
        + " revmatpr="
        + str(args.revmatpr)
        + ";\n"
    )
    outfile.write(
        "\tmcmc ngen="
        + str(args.ngen)
        + " samplefreq="
        + str(args.samplefreq)
        + " printfreq="
        + str(args.printfreq)
        + " burninfrac="
        + str(args.burninfrac)
        + " nchains="
        + str(args.nchains)
        + " nruns="
        + str(args.nruns)
        + ";\n"
    )
    outfile.write("\tsumt;\n")
    outfile.write("end;\n\n")
    return


# Generates the block if all mcmc runs have the same parameters (only one argument specified)
def genblock(outfile, args):
    filenames = args.inpath
    for f in filenames:
        outfile.write("begin mrbayes;\n")
        outfile.write(
            "\tset autoclose="
            + str(args.autoclose)
            + " nowarnings="
            + str(args.nowarnings)
            + " seed="
            + str(args.seed)
            + ";\n"
        )
        outfile.write("\texecute " + str(f) + ";\n")
        paraminputs(outfile, args)
    return


# Generates the block if user wants to have different parameters for each mcmc run (multiple arguments specified)
def genblock2(outfile, params, args):
    filenames = args.inpath
    arg_array = array(params)
    t_array = transpose(arg_array)
    for row, f in zip(t_array, filenames):
        outfile.write("begin mrbayes;\n")
        outfile.write(
            "\tset autoclose=" + str(row[13]) + " seed=" + str(row[15]) + " nowarnings=" + str(row[14]) + ";\n"
        )
        outfile.write("\texecute " + str(f) + ";\n")
        outfile.write(
            "\tlset nst="
            + str(row[0])
            + " rates="
            + str(row[1])
            + " ngammacat="
            + str(row[2])
            + ";\n"
        )
        outfile.write(
            "\tprset brlenspr="
            + str(row[3])
            + " shapepr="
            + str(row[4])
            + " statefreqpr="
            + str(row[5])
            + " revmatpr="
            + str(row[6])
            + ";\n"
        )
        outfile.write(
            "\tmcmc ngen="
            + str(row[7])
            + " samplefreq="
            + str(row[8])
            + " printfreq="
            + str(row[9])
            + " burninfrac="
            + str(row[10])
            + " nchains="
            + str(row[11])
            + " nruns="
            + str(row[12])
            + ";\n"
        )
        outfile.write("\tsumt;\n")
        outfile.write("end;\n\n")


# Executes above functions and writes the output file
def main(args):
    params_list = [
        args.nst,
        args.rates,
        args.ngammacat,
        args.brlenspr,
        args.shapepr,
        args.statefreqpr,
        args.revmatpr,
        args.ngen,
        args.samplefreq,
        args.printfreq,
        args.burninfrac,
        args.nchains,
        args.nruns,
        args.autoclose,
        args.nowarnings,
        args.seed,
    ]
    arg_lengths = sum(len(a) for a in params_list)
    print("Creating MrBayes blocks...")
    if arg_lengths == 16:
        with open(args.outfile + ".nexus", "a+") as mbblocks:
            genblock(mbblocks, args)
        with open(args.outfile + ".nexus", "r+") as convert:
            lines = convert.read()
            converted = lines.replace("[", "").replace("'", "").replace("]", "")
        with open(args.outfile + ".nexus", "w+") as mbblocks:
            mbblocks.write(converted)
    else:
        with open(args.outfile + ".nexus", "a+") as mbblocks:
            genblock2(mbblocks, params_list, args)
    print("Done.")


if __name__ == "__main__":
    args = readArguments()
    main(args)
