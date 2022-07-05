#!/usr/bin/env nextflow

params.inputsearchresults = ''
params.workflowParameters = ''
params.standardfile = "MSMLS_HILICz150mm_Annotation20190824_Template_QCv3_Unlabeled_Positive.csv"

//Params
params.rt_tolerance = '0.1' // This is a tolerance in minutes

_inputresults_ch = Channel.fromPath( params.inputsearchresults + "/*" )

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

process calculateResults {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file input_result from _inputresults_ch.first()

    output:
    file "result_file.tsv"
    file "filtered_results.tsv"

    """
    python $TOOL_FOLDER/template_script.py \
        $TOOL_FOLDER/$params.standardfile \
        "$input_result" \
        "result_file.tsv" \
        --output_filtered_results_filename filtered_results.tsv \
        --rt_tolerance $params.rt_tolerance
    """
}
