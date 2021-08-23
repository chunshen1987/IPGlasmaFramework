#!/usr/bin/env bash

usage="./collect_singularity_events.sh fromFolder toFolder"

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
cp -r ${fromFolder}/model_parameters ${target_folder}/
target_res_folder=${target_folder}/RESULTS
mkdir -p ${target_res_folder}

total_eventNum=0
collected_eventNum=0
for ijob in `ls --color=none $fromFolder | grep "event" `;
do
    eventsPath=${fromFolder}/${ijob}
    for iev in `ls --color=none $eventsPath | grep RESULTS_*.h5`
    do
        echo $iev
        mv ${eventsPath}/${iev} $target_res_folder
        ((collected_eventNum++))
    done
done

echo "Collected events number: " $collected_eventNum

if [ -f ${target_folder}/${folderName}.h5 ]; then
    mv ${target_folder}/${folderName}.h5 ${target_res_folder}
fi
./combine_multiple_hdf5.py ${target_res_folder}
mv RESULTS.h5 ${target_folder}/${folderName}.h5
rm -fr $target_res_folder
