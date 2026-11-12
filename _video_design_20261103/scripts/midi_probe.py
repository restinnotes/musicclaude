import pretty_midi,sys,json,re
sys.stdout.reconfigure(encoding='utf-8')
R=r"D:\music-experience-pipeline\runs\production\frederic-chopin-barcarolle-in-f-sharp-major-op-6-b1ce4fc10b1b\music\alignment\performance_warped.mid"
pm=pretty_midi.PrettyMIDI(R)
print('tracks',len(pm.instruments),'end',round(pm.get_end_time(),2))
for i in pm.instruments[:12]:
    print(repr(i.name),i.program,len(i.notes),'vel',min(n.velocity for n in i.notes),max(n.velocity for n in i.notes),'pitch',min(n.pitch for n in i.notes),max(n.pitch for n in i.notes),'first',round(i.notes[0].start,2))
