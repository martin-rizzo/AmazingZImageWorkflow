#!/usr/bin/env bash
# File    : release.sh
# Purpose : Release script for the AmazingZImageWorkflow project
# Author  : Martin Rizzo | <martinrizzo@gmail.com>
# Date    : Dec 12, 2025
# Repo    : https://github.com/martin-rizzo/AmazingZImageWorkflow
# License : Unlicense
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                           Amazing Z-Image Workflow
#  Z-Image workflow with customizable image styles and GPU-friendly versions
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _


# Builds a zip file containing specific workflow files and associated images.
#
# Usage:
#   build_zip_file <ZIP_FILE> <WORKFLOW>
#
# Parameters:
#   ZIP_FILE: The path to the output zip file.
#   WORKFLOW: The base name of the workflow (e.g., "amazing-z-image").
#
# The function collects the following files:
#   - "${workflow}_GGUF.json"
#   - "${workflow}_SAFETENSORS.json"
#   - "LICENSE"
#   - The file "files/amazing-z-readme.txt          (renamed to "README.TXT")
#   - The file "${workflow}_styles.txt"             (renamed to "styles.txt")
#   - All files matching "${workflow}_styles*.jpg"  (renamed to "styles*.jpg")
#
# Example:
#   build_zip_file workflow.zip amazing-z-image
#
build_zip_file() {
    local zip_file="$1"
    local workflow="$2"
    local temp_files=() #< to keep track of temporary files
    local gallery="${workflow}_styles"
    local gallery_ext=".jpg"
    local filename

    # file name suffixes regarding the format of the checkpoint file
    local formats=( "_GGUF" "_SAFETENSORS" )

    # file name suffixes relating to different variants of the same workflow
    local variations=( "" "-a" "-b" "-c" "-d" "-e" "-f" )

    # in this array, we collect all the files that are part of the release package
    local zip_content=(
        "LICENSE"
    )

    # loop through all variations that the workflow can have (adding the available suffixes)
    for variation in "${variations[@]}"; do
        for format in "${formats[@]}"; do
            filename="${workflow}${variation}${format}.json"
            [[ -f "$filename" ]] && zip_content+=( "${filename}" )
        done
    done

    # copy temporarily "README.TXT" file from /files directory
    cp "files/amazing-z-readme.txt" "README.TXT"
    temp_files+=( "README.TXT" )

    # copy "styles.txt" file
    cp "${gallery}.txt" "styles.txt"
    temp_files+=( "styles.txt" )

    echo "release.sh is under development."  #< placeholder until the function is implemented properly
    exit 1

    # # collect gallery images renaming them to "styles1.jpg", "styles2.jpg", etc.
    # for file in "${gallery}"*"${gallery_ext}"; do
    #     [[ -f "$file" ]] || continue  #< ensure it's a valid file

    #     # extract the numeric suffix from the filename
    #     index=${file#"$gallery"}
    #     index=${index%"$gallery_ext"}

    #     # create temporary image file (e.g., "styles1.jpg")
    #     image="styles${index}.jpg"
    #     cp "$file" "$image"
    #     temp_files+=( "$image" )
    # done

    # # create the zip archive with the collected files
    # zip -j "$zip_file" "${zip_content[@]}" "${temp_files[@]}"

    # # remove temporary files
    # rm "${temp_files[@]}"
}


# Builds the release package for each workflow
#
# Usage:
#   build_release_packages [VERSION] [OUTPUT_DIR]
#
# Parameters:
#   VERSION    : The version string (e.g., "v1.2.3"). Defaults to "v1.2.3".
#   OUTPUT_DIR : The directory where the ZIP files will be saved. Defaults to "/tmp/amazing_release".
#
# Example:
#   build_release_packages "v1.2.0" "/tmp/amazing_release"
#
build_release_packages() {
    local VERSION=${1:-v1.2.3}
    local OUTPUT_DIR=${2:-/tmp/amazing_release}
    local MAJOR MINOR
    MAJOR=$(echo "${VERSION##v}" | cut -d '.' -f1)
    MINOR=$(echo "${VERSION##v}" | cut -d '.' -f2)

    build_zip_file "$OUTPUT_DIR/amazingZImage_v${MAJOR}${MINOR}.zip"  amazing-z-image
    build_zip_file "$OUTPUT_DIR/amazingZComics_v${MAJOR}${MINOR}.zip" amazing-z-comics
    build_zip_file "$OUTPUT_DIR/amazingZPhoto_v${MAJOR}${MINOR}.zip"  amazing-z-photo
}


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#
# The "RELEASE_DIR" variable is exported so it can be used by github workflow.

# generate the release directory taking as base the second argument
# (if the second parameter is not provided, use '/tmp/amazing_release')
export RELEASE_DIR="${2:-/tmp}/amazing_release"
mkdir -p "$RELEASE_DIR"

# calls "build_release_packages"
#  - the first parameter is the version,
#  - the second parameter is the output directory.
build_release_packages "$1" "$RELEASE_DIR"

# prints a message with the location of zip archives
echo
echo "The files were created in: $RELEASE_DIR"
echo
