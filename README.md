# MidiCommunication

Important Dependencies :
  1) Install Python 2.7 (Add it to the path in environmental variables if working on windows) - Link :https://www.python.org/download/releases/2.7/
  2) After Installing Python , These are the libraries which are required along with it :
     a) Install Kivy - Installation guide : https://kivy.org/doc/stable/installation/installation-windows.html      
     b) Install Mido - Installation guide : https://mido.readthedocs.io/en/latest/installing.html
  3) Install loopMidi - Link : https://www.tobias-erichsen.de/software/loopmidi.html
  
Note : 
  1) Run LoopMidi before running the software
  2) Create a new port in LoopMidi
  3) Disable Feedback Dectection in LoopMidi ( Open LoopMidi , Go to Advanced Section and disable Feedback Decection)
  4) If you want to use it along with the Unreal Engine then install "ProceduralMidi" ( Free Plugin) in the engine and enable it and use it to define where to read messages in the engine using BluePrints/Scripts.

How to Run:
  1) Go to Scripts and Run SendData.py
  2) In the UI Enter the path of the file to read (Must be a csv file) and the Port name.
  3) After Doing this you need to Preprocess the file before pressing start.
  4) You can print Column names to define the settings of sending the data
  5) You can define the delay , no. of rows to send as a single message and Interpolation between two packets.
  6) After setting up everything you can press start.
  
Things to know about Messages you can send:
  1) The messages sent are send using midi communication
  2) The messages have value between 0 to 127 . ( Values are automatically normalized to this range if your csv file have a different range than this.)
  3) You can send 2 type of messages :
      a) NoteOn Messages : It contains two values "Note" and "Velocity". You can select which column of your csv file represents Note and which column of your file represents Velocity.
      b) CC Messages : It contains two values "Control" and "Value" . Control is like a tunnel you can select where the values will be sent. Eg. 33 may be you Control and on this control you can send values between 0-127 and as many as you want. Note : Control must be in between 0-127
  4) You can read more about these messages here : https://www.midi.org/articles-old/about-midi-part-3-midi-messages
  
