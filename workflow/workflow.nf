#!/usr/bin/env nextflow

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

// Proteosafe param
params.workflowParameters = ''

// workflow params
params.inputsearchresults = ''
params.standardfile = "HILIC_standards_positive.tsv"            // CUSTOMFILE enables the second one
params.standardfile_custom = "folder_name"   // This is if we want to use a custom file, mostly a proteosafe customization

if (params.standardfile == "CUSTOMFILE") {
    _standardfile_ch = Channel.fromPath( params.standardfile_custom + "/*.tsv" )
}
else{
    _standardfile_ch = Channel.fromPath( TOOL_FOLDER + "/" + params.standardfile )
}

// These are override model parameters
params.override = "No" // OVERRIDE will use the user set values
params.override_slope = 1
params.override_intercept = 0 

//Params
params.rt_tolerance = '0.3' // This is a tolerance in minutes
params.rt_min = '0.0' // This is a minimum in minutes
params.rt_max = '50' // This is a maximum in minutes

_inputresults_ch = Channel.fromPath( params.inputsearchresults + "/*" )



process calculateResults {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file input_result from _inputresults_ch.first()
    file standardfile from _standardfile_ch.first()

    output:
    file "result_file.tsv"
    file "filtered_results.tsv"
    file "output_results_scatter.html"

    """
    python $TOOL_FOLDER/template_script.py \
        $standardfile \
        "$input_result" \
        "result_file.tsv" \
        --output_filtered_results_filename filtered_results.tsv \
        --output_results_scatter output_results_scatter.html \
        --rt_tolerance $params.rt_tolerance \
        --rt_min $params.rt_min \
        --rt_max $params.rt_max \
        --override $params.override \
        --override_slope $params.override_slope \
        --override_intercept $params.override_intercept
    """
}
