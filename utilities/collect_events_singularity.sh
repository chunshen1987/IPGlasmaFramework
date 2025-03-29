#!/usr/bin/env bash

usage="$0 fromFolder toFolder"

fromFolder=$1
toFolder=$2

if [ -z "$fromFolder" ]
then
    echo $usage
    exit 1
fi
if [ -z "$toFolder" ]
then
    echo $usage
    exit 1
fi

fromFolder=${fromFolder%"/"}
toFolder=${toFolder%"/"}

echo "collecting events from " $fromFolder " to " $toFolder

folderName=`echo $fromFolder | rev | cut -d "/" -f 1 | rev`
target_folder=${toFolder}/${folderName}
mkdir -p ${target_folder}
cp ${fromFolder}/parameter* ${target_folder}/
target_spvn_folder=${target_folder}/SPVN_RESULTS
mkdir -p ${target_spvn_folder}

spvn_folder_name="spvn_results_"

for ijob in `ls --color=none $fromFolder | grep "event" `;
do
    eventsPath=${fromFolder}/${ijob}
    for iev in `ls --color=none ${eventsPath} | grep "RESULTS"`
    do
        mv ${eventsPath}/${iev} $target_spvn_folder
    done
done

if [ -f ${target_folder}/${folderName}.h5 ]; then
    mv ${target_folder}/${folderName}.h5 ${target_spvn_folder}
fi
./combine_multiple_hdf5.py ${target_spvn_folder}
mv SPVN_RESULTS.h5 ${target_folder}/${folderName}.h5
rm -fr $target_spvn_folder
