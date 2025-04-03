'''
Implement GUI for SIP Client

Task to do:
1. Add Start Call/End Call buttons.
2. Trigger SIP signaling and RTP Streaming from GUI.
3. Display real-time logs (call status, packet info).
'''


from tkinter import *

windows = Tk()
windows.title("SIP Client")
windows.configure(bg="lightblue")
windows.resizable(False, False)
windows.geometry("400x800")

# Add buttons for SIP signaling and RTP streaming
start_call_button = Button(windows, text="Start Call", width=20, height=2, bg="green", fg="white")
start_call_button.pack(pady=20)
end_call_button = Button(windows, text="End Call", width=20, height=2, bg="red", fg="white")
end_call_button.pack(pady=20)

# Add a text area for real-time logs
log_area = Text(windows, width=50, height=20, bg="white", fg="black")
log_area.pack(pady=20)
log_area.insert(END, "Real-time logs will appear here...\n")

windows.mainloop()