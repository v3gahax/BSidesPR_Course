import socket

def send_hl7_message(host, port, hl7_message):
    """
    Send an HL7 message to a specified host and port.
    """
    # MLLP start and end block characters, and the carriage return.
    start_block = '\x0b'
    end_block = '\x1c'
    carriage_return = '\r'
    mllp_message = f"{start_block}{hl7_message}{end_block}{carriage_return}"

    # Create a socket and connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(mllp_message.encode('utf-8'))
        print("HL7 message sent to the server.")

if __name__ == "__main__":
    # Server's IP address and port number
    HOST = '172.16.0.126'  # or the server's IP address if different
    PORT = 2575  # The port used by the server

    # Example HL7 message (ensure it's in the correct format for your server)
    hl7_message = "MSH|^~\\&|GHH_ADT||||20080115153000||ADT^A01^ADT_A01|0123456789|P|2.5||||AL|\r" \
              "EVN||20080115153000||AAA|AAA|20080114003000|\r" \
              "PID|1||566-554-3423^^^GHH^MR||EVERYMAN^ADAM^A|||M|||2222 HOME STREET^^ANN ARBOR^MI^^USA||555-555-2004~444-333-222|||M|\r" \
              "NK1|1|NUCLEAR^NELDA^W|SPO|2222 HOME STREET^^ANN ARBOR^MI^^USA|\r" \
              "PV1|1|I|GHH PATIENT WARD|U||||^SENDER^SAM^^MD|^PUMP^PATRICK^P|CAR||||2|A0|||||||||||||||||||||||||||||2008|\r" \
              "IN1|1|HCID-GL^GLOBAL|HCID-23432|HC PAYOR, INC.|5555 INSURERS CIRCLE^^ANN ARBOR^MI^99999^USA||||||||||||||||||||||||||||||||||||||||||||444-33-3333"

    # Send the message
    send_hl7_message(HOST, PORT, hl7_message)
