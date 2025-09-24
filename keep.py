#!/usr/bin/env python

import os
import json
from time import sleep
from dotenv import load_dotenv
import gkeepapi
import datetime
from gkeepapi.node import NodeLabels, NodeType, Label

load_dotenv()

# Obtain a master token for your account (see docs)
fromEmailAddress = os.getenv('SOURCE_EMAIL')
fromMasterToken = os.getenv('SOURCE_MASTER_TOKEN')
toEmailAddress = os.getenv('DEST_EMAIL')
toMasterToken = os.getenv('DEST_MASTER_TOKEN')
debugMode = False

print('Authenticating [Source]:', fromEmailAddress)
sourceKeep = gkeepapi.Keep()
localDir = os.getcwd() + '/.dumps'
localName = f"{localDir}/{fromEmailAddress.lower()}.keep.json"

if not os.path.exists(localDir):
    os.mkdir(localDir, mode=0o755)

if localName and os.path.isfile(localName) and os.path.getsize(localName) > 1:
    isLocalLoad = True
    print(f'Grabbing Local: {localName}')
    sourceKeep.authenticate(fromEmailAddress, fromMasterToken, json.load(open(localName, 'r')), False)
else:
    sourceKeep.authenticate(fromEmailAddress, fromMasterToken)
    json.dump(sourceKeep.dump(), open(localName, 'w'), indent=2)


print('Authenticating [Destination]:', toEmailAddress)
destKeep = gkeepapi.Keep()
try:
    destKeep.authenticate(toEmailAddress, toMasterToken)
except gkeepapi.exception.APIException as e:
    print(f'Error Occurred during Auth. {str(e)}')
    exit(1)

"""
Find or Creates New Label 
"""
def findOrCreateLabel (name: str) -> Label:
    found = destKeep.findLabel(name)
    if found is None:
        found = destKeep.createLabel(name)
    return found

def prepareLabels(sourceLabels: NodeLabels, created: datetime.datetime) -> list[Label] | None:
    destLabels: list[Label] = []
    if sourceLabels and len(sourceLabels.all()) > 0:
        for oneLabel in sourceLabels.all():
            found = destKeep.findLabel(oneLabel.name)
            if found is None:
                found = destKeep.createLabel(oneLabel.name)
            destLabels.append(found)
    destLabels.append(findOrCreateLabel(created.strftime("%Y")))
    destLabels.append(findOrCreateLabel(created.strftime("%Y %B")))
    return destLabels

def getImportedLabel(name: str = fromEmailAddress) -> Label:
    found = destKeep.findLabel(name)
    return found if found is not None else destKeep.createLabel(name)

def getListChildren(items: NodeType.List) -> list[tuple[str,bool]]:
    bag = []
    if len(items) > 0:
        for one in items:
            bag.append((one.text, one.checked))
    return bag


allNotes = sourceKeep.all()[::-1]
total = len(allNotes)
index = 1
batchSize = 500


for item in allNotes:
    title = item.title if item.title != '' else item.text.split('\n')[0]
    # if item.type not in types:
    #    types.append(item.type)
    print(f'{index}/{total}: {title}')
    if item.type == NodeType.List:
        li = getListChildren(item.items)
        note = destKeep.createList(item.title, li)
    else:
        note = destKeep.createNote(item.title, item.text)
    note.labels.add(getImportedLabel())
    note.pinned = item.pinned
    note.color = item.color
    note.archived = item.archived
    labels = prepareLabels(item.labels, item.timestamps.edited)
    if labels is not None:
        for oneLabel in labels:
            note.labels.add(oneLabel)
    """if item.type == NodeType.List:
        newLabels = []
        for n in note.labels.all():
            newLabels.append(n.name)
        if len(newLabels) > 3:
            print(newLabels)
        """
    if not debugMode and (index % batchSize == 0 or index == total):
        print(f'{index}/{total} Syncing changes to {toEmailAddress}')
        success = False
        delayRegular = 5
        errorDelay = 0
        while not success:
            try:
                destKeep.sync()
                success = True
                print(f'Waiting for {delayRegular} seconds to avoid hitting rate limit')
                sleep(delayRegular)
            except gkeepapi.exception.APIException as e:
                errorDelay = min(errorDelay + 10, 60)
                print(f'Error Occurred: {str(e)}')
                print(f'Sleeping for {errorDelay}seconds {str(e)}')
                sleep(errorDelay)
    index += 1

# Generate requirements.txt
# pipreqs --force --ignore .dumps,.venv .
