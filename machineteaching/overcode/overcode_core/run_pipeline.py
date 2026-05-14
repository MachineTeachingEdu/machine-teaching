import argparse
from os import path
import pipeline_preprocessing
import pipeline

def run_pipeline(basedir, run_pre=True, funcname='test', run_pipeline=True, distances=True, output_only=False):
    """
    Run the data preprocessing pipeline and analysis pipeline for a given target directory.

    Args:
        basedir (str): Path to a directory containing a 'data' subdirectory (containing students solutions and answer.py) 
                       and a 'testCase.py' file.

        run_pre (bool, optional): Whether to run the preprocessor. Default is True.

        funcname (str, optional): The name of the function that is being tested. Calls to the named function
                                  will be removed from student code during the tidying step in the preprocessor.
                                  Default is 'test'.

        run_pipeline (bool, optional): Whether to run the analysis pipeline. Will not work if the preprocessor
                                       has never been run. Default is True.

        distances (bool, optional): Include to calculate pairwise distances between all stacks. Default is True.

        output_only (bool, optional): Include to only calculate output during pre-processing pipeline. Default is False.

    Returns:
        None
    """

    # The data subdirectory
    datadir = path.join(basedir, 'data')

    # The testCase.py file
    testcasePath = path.join(basedir, 'testCase.py')

    # We won't be using JSON with Machine Teaching, so this is always False
    jsonPath = False

    # preprocess
    if run_pre:
        if output_only:
            print('Only output traced during preprocessor run.')
        pipeline_preprocessing.preprocess_pipeline_data(
            datadir,
            testcasePath,
            output_only,
            funcname,
            jsonPath,
            None  # The value 'None' is not used here
        )

    # Run the analysis pipeline
    if run_pipeline:
        outputPath = path.join(basedir, 'output')
        pipeline.run(datadir, outputPath, distances)

if __name__ == "__main__":
    # Add possible options to the command line interface
    parser = argparse.ArgumentParser()
    parser.add_argument('basedir', metavar='TARGET_DIR',
                        help='Path to a directory containing a data subdirectory and a testCase.py file')

    # preprocessor & arguments
    parser.add_argument('-P', '--run-pre', action='store_true',
                        help='Run the preprocessor.')
    parser.add_argument('-n', '--funcname', default='test', metavar='NAME',
                        help='The name of the function that is being tested. Calls to the named ' +
                             'function will be removed from student code during the tidying step ' +
                             'in the preprocessor.')

    # pipeline & arguments
    parser.add_argument('-p', '--run-pipeline', action='store_true',
                        help='Run the analysis pipeline. Will not work if the preprocessor has ' +
                             'never been run.')
    parser.add_argument('-d', '--distances', action='store_true',
                        help='Include to calculate pairwise distances between all stacks.')
    parser.add_argument('-t', '--output-only', action='store_true',
                        help='Include to only calculate output during pre-processing pipeline.')

    args = parser.parse_args()

    run_pipeline(args.basedir, args.run_pre, args.funcname, args.run_pipeline, args.distances, args.output_only)

