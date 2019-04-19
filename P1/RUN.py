
from part1 import PreProcessing
from part2 import LpcProcessing
from part3 import Synthesizer
from part4 import Coder
from part5 import Decoder
from part6 import Analysis



PreProcessing().run()
LpcProcessing().run()
Synthesizer().run()
Coder().run()
Decoder().run()
an = Analysis()
an.compareVisu()
#an.compareAudio()