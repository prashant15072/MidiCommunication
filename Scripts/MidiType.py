class MidiType:

    def __init__(self,type,channel):
        self.type=type
        self.channel=channel

    def getType(self):
        return self.type

    def getChannel(self):
        return self.channel



class ControlChange(MidiType):

    def __init__(self,channel,control,value):
        MidiType.__init__(self,"control_change",channel)
        self.control=control
        self.value=value

    def getControl(self):
        return self.control

    def getValue(self):
        return self.value


class NoteOn(MidiType):

    def __init__(self,channel,note,velocity):
        MidiType.__init__(self,"note_on",channel)
        self.note=note
        self.velocity=velocity

    def getNote(self):
        return self.note

    def getVelocity(self):
        return self.velocity

