#!/usr/bin/env python

import os
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

sourceKeep = gkeepapi.Keep()
destKeep = gkeepapi.Keep()
print('Authenticating [Source]:', fromEmailAddress)
sourceSuccess = sourceKeep.authenticate(fromEmailAddress, fromMasterToken)
print('Authenticating [Destination]:', toEmailAddress)
destSuccess = destKeep.authenticate(toEmailAddress, toMasterToken)
# old = all[-1]

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
    if sourceLabels is None or len(sourceLabels) < 1:
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
# types = []
# json.dump(sourceKeep.dump(), open('localKeep.json', 'w'), indent=2)
for item in allNotes:
    title = item.title if item.title != '' else item.text.split('\n')[0]
    # if item.type not in types:
    #    types.append(item.type)
    print(f'{index}/{total}: {title}')
    if item.type == NodeType.List:
        li = getListChildren(item.items)
        note = destKeep.createList(item.title, li)
        # note.items = item.list
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
    if item.type == NodeType.List:
        # print(f'{index}/{total}: {title}')
        newLabels = []
        for n in note.labels.all():
            newLabels.append(n.name)
        # print(newLabels)
        # print(note.text)
    index += 1

# print(types)
print(f'Saving changes to {toEmailAddress}...')
destKeep.sync()
