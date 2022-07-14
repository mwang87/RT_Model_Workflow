#!/usr/bin/env nextflow

params.inputsearchresults = ''
params.workflowParameters = ''
params.standardfile = "HILIC_standards_positive.tsv" 

// These are override model parameters
params.override = "No" // OVERRIDE will use the user set values
params.override_slope = 1
params.override_intercept = 0 

//Params
params.rt_tolerance = '0.3' // This is a tolerance in minutes

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
    file "output_results_scatter.html"

    """
    python $TOOL_FOLDER/template_script.py \
        $TOOL_FOLDER/$params.standardfile \
        "$input_result" \
        "result_file.tsv" \
        --output_filtered_results_filename filtered_results.tsv \
        --output_results_scatter output_results_scatter.html \
        --rt_tolerance $params.rt_tolerance \
        --override $params.override \
        --override_slope $params.override_slope \
        --override_intercept $params.override_intercept
    """
}
