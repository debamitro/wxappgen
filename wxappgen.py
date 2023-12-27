#!python3

class App_files_generator:
    def print_wx_include(self, f):
        print("#include \"wx/wx.h\"", file=f)

    def print_wx_statusbar_include(self, f):
        print ("#include \"wx/statusbr.h\"", file=f)
    
    def print_wx_thread_include(self, f):
        print ("#include \"wx/thread.h\"", file=f)

    def print_header_guard_open (self, headerName, f):
        print ("#ifndef {}\n#define {}\n".format(headerName, headerName), file=f)

    def print_doxygen_file (self, filename, f):
        print ("/// @file {}".format (filename), file=f)
        print ("/// @author {}\n".format(self.author), file=f)
        
    def __init__ (self, name, author, prefix, statusbar_y, threaded_y):
        self.prefix = prefix
        self.statusbar_y = statusbar_y
        self.name = name
        self.author = author
        self.threaded = threaded_y

    def print_app_include(self, f):
        print("#include \"{}App.hh\"".format(self.prefix), file=f)

    def print_frame_include(self, f):
        print("#include \"{}Frame.hh\"".format(self.prefix), file=f)

    def print_implement_app(self, f):
        print("\nwxIMPLEMENT_APP({}App);".format(self.prefix), file=f)

    def print_app_class_header (self, f):
        appName = "{}App".format(self.prefix)
        print ("\n/// {} represents the application state".format(appName), file=f)
        print ("class {} : public wxApp".format(appName), file=f)
        print ("{{\npublic:\n    {} () = default;\n    ~{} () = default;\n".format(appName, appName), file=f)
        print ("    /// Boiler-plate initialization of the application", file=f)
        print("    bool OnInit ();\n};", file=f)

    def print_app_oninit (self, f):
        print ("\nbool {}App::OnInit ()".format(self.prefix), file=f)
        print (
"""{
    if (!wxApp::OnInit())
    {
        return false;
    }
""", file=f)
        print ("    auto frame = new {}Frame();".format(self.prefix), file=f)
        print (
"""    frame->Show (true);

    return true;
}
""", file=f)

    def print_frame_class_header (self, f):
        frameName = "{}Frame".format(self.prefix)
        print ("\n/// {} represents the main window of the application".format(frameName), file=f)
        print("class {}: public wxFrame".format(frameName), end='', file=f)
        if self.threaded == "Y":
            print (", wxThreadHelper", file=f)
        print ("{", file=f)
        print("public:\n    {} ();".format(frameName), file=f)
        print("    ~{} () = default;\n".format(frameName), file=f)
        print("private:", file=f)
        if self.threaded == "Y":
            print ("    /// This gets called in the child thread", file=f)
            print ("    wxThread::ExitCode Entry ();", file=f)
        if self.statusbar_y == "Y":
            print("    wxStatusBar* statusbar_;", file=f)
        print("    wxDECLARE_EVENT_TABLE ();\n};", file=f)

    def print_frame_event_table (self, f):
        print ("\nwxBEGIN_EVENT_TABLE({}Frame, wxFrame)".format(self.prefix), file=f)
        print ("wxEND_EVENT_TABLE()", file=f)

    def print_frame_class_definitions (self, f):
        print ("\n{}Frame::{}Frame () :".format(self.prefix, self.prefix), file=f)
        print ("    wxFrame (nullptr, wxID_ANY, \"{}\")".format(self.name), end='', file=f)
        if self.statusbar_y == "Y":
            print (",\n    statusbar_ (nullptr)", file=f)
        print ("\n{", file=f)
        if self.statusbar_y == "Y":
            print ("""    statusbar_ = new wxStatusBar (this, wxID_ANY);
    statusbar_->SetFieldsCount (2);
    SetStatusBar (statusbar_);
""", file=f)
        print ("}", file=f)
        if self.threaded == "Y":
            print ("\nwxThread::ExitCode {}Frame::Entry ()".format(self.prefix), file=f)
            print ("{\n    // Your implementation here\n    return 0;\n}", file=f)

    def generate (self):
        with open ('main.cc','w') as f:
            self.print_doxygen_file ('main.cc', f)
            self.print_wx_include (f)
            self.print_app_include (f)
            self.print_implement_app (f)
        with open ("{}App.hh".format(self.prefix), 'w') as f:
            self.print_header_guard_open ("{}APP_HH".format(self.prefix.upper()), f)
            self.print_doxygen_file ("{}App.hh".format(self.prefix), f)
            self.print_wx_include (f)
            self.print_app_class_header (f)
            print ("\n#endif", file=f)
        with open ("{}App.cc".format(self.prefix), 'w') as f:
            self.print_doxygen_file ("{}App.cc".format(self.prefix), f)
            self.print_wx_include (f)
            self.print_app_include (f)
            self.print_frame_include (f)
            self.print_app_oninit (f)
        with open ("{}Frame.hh".format(self.prefix), 'w') as f:
            self.print_header_guard_open ("{}FRAME_HH".format(self.prefix.upper()), f)
            self.print_doxygen_file ("{}Frame.hh".format(self.prefix), f)
            self.print_wx_include (f)
            if self.statusbar_y == "Y":
                self.print_wx_statusbar_include (f)
            if self.threaded == "Y":
                self.print_wx_thread_include (f)
            self.print_frame_class_header (f)
            print ("\n#endif", file=f)
        with open ("{}Frame.cc".format(self.prefix), 'w') as f:
            self.print_doxygen_file ("{}Frame.cc".format(self.prefix), f)
            self.print_wx_include (f)
            self.print_frame_include (f)
            self.print_frame_event_table (f)
            self.print_frame_class_definitions (f)
        with open ("Makefile", 'w') as f:
            print("""
CFLAGS := `$(WX_HOME)/wx-config --cflags` -std=c++14 -g
LIBS := `$(WX_HOME)/wx-config --libs core,base,adv`
""", file=f)
            print ("all: {}app\n".format(self.prefix.lower()), file=f)
            print ("clean:\n\t$(RM) {}app *.o".format(self.prefix.lower()), file=f)
            print ("{}app: main.o {}App.o {}Frame.o\n".format(self.prefix.lower(),self.prefix,self.prefix), file=f)
            print ("\t$(CXX) $(LIBS) -o $@ main.o {}App.o {}Frame.o".format(self.prefix,self.prefix), file=f)
            print ("""
%.o: %.cc
	$(CXX) $(CFLAGS) -c -o $@ $<
""", file=f)
        with open ("README.md", 'w') as f:
            print ("# {}".format(self.name),file=f)
            print ("""## How to build

You need to set WX_HOME to the wxWidgets build directory, and invoke make.
Example:

```
make WX_HOME=<path-to-wxWidgets-directory>/build-cocoa
```
""", file=f)
        

if __name__ == "__main__":
    print ("wxWidgets skeleton app generator\n")
    name = input ('What is the name of your app? ')
    author = input ('Who is the author? ')
    prefix = input('What is the prefix you want to use? ')
    statusbar_y = input('Do you need a statusbar? (Y/n) ')
    if statusbar_y == "N" or statusbar_y == "n":
        statusbar_y = "N"
    else:
        statusbar_y = "Y"
    threaded_y = input('Do you need threads? (Y/n) ')
    if threaded_y == "N" or threaded_y == "n":
        threaded_y = "N"
    else:
        threaded_y = "Y"
    generator = App_files_generator (name, author, prefix, statusbar_y, threaded_y)
    generator.generate ()

    
