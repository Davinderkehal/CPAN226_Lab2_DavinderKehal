# This program was modified by Davinder Kehal / N01718686

import socket
import argparse
import struct  # IMPROVEMENT: Used to pack/unpack sequence numbers

def run_server(port, output_file):
    # 1. Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IMPROVEMENT: Create UDP socket

    # 2. Bind socket to the given port
    server_address = ('', port)                              # IMPROVEMENT: Bind to all interfaces
    sock.bind(server_address)                                # IMPROVEMENT: Activate socket binding
    print(f"[*] Server listening on port {port}")            # IMPROVEMENT: Status message

    try:
        while True:
            f = None                                         # IMPROVEMENT: File handle
            expected_seq = 0                                 # IMPROVEMENT: Track expected sequence
            buffer = {}                                      # IMPROVEMENT: Buffer out-of-order packets
            sender_filename = None                           # IMPROVEMENT: Output file name

            print("==== Start of reception ====")             # IMPROVEMENT: Start marker

            while True:
                packet, addr = sock.recvfrom(2048)           # IMPROVEMENT: Receive UDP packet

                seq_num = struct.unpack("!I", packet[:4])[0] # IMPROVEMENT: Extract sequence number
                payload = packet[4:]                          # IMPROVEMENT: Extract payload data

                # EOF detection (header only, no payload)
                if len(payload) == 0:                         # IMPROVEMENT: Detect EOF packet
                    sock.sendto(struct.pack("!I", seq_num), addr)  # IMPROVEMENT: ACK EOF
                    print(f"[*] End of file signal received from {addr}")  # IMPROVEMENT: Log EOF
                    break                                    # IMPROVEMENT: Exit receive loop

                # Open file on first packet
                if f is None:
                    ip, sender_port = addr                   # IMPROVEMENT: Extract sender info
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"  # IMPROVEMENT: File name
                    f = open(sender_filename, 'wb')          # IMPROVEMENT: Open file
                    print(f"[*] First packet received from {addr}. Writing to '{sender_filename}'")  # IMPROVEMENT

                # Send ACK immediately (Stop-and-Wait requirement)
                sock.sendto(struct.pack("!I", seq_num), addr)  # IMPROVEMENT: Send ACK

                # In-order packet
                if seq_num == expected_seq:                  # IMPROVEMENT: Correct packet arrived
                    f.write(payload)                         # IMPROVEMENT: Write in-order data
                    expected_seq += 1                        # IMPROVEMENT: Advance expected sequence

                    # Flush buffered packets
                    while expected_seq in buffer:            # IMPROVEMENT: Check buffer
                        f.write(buffer.pop(expected_seq))   # IMPROVEMENT: Write buffered packet
                        expected_seq += 1                    # IMPROVEMENT: Advance sequence

                # Out-of-order packet
                elif seq_num > expected_seq:                 # IMPROVEMENT: Packet arrived early
                    buffer[seq_num] = payload                # IMPROVEMENT: Store in buffer

                # Duplicate packet
                else:
                    pass                                     # IMPROVEMENT: Ignore duplicate packet

            if f:
                f.close()                                    # IMPROVEMENT: Close file after reception
                print("==== End of reception ====")           # IMPROVEMENT: End marker

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")               # IMPROVEMENT: Handle CTRL+C
    except Exception as e:
        print(f"[!] Error: {e}")                              # IMPROVEMENT: Error handling
    finally:
        sock.close()                                          # IMPROVEMENT: Close socket
        print("[*] Server socket closed.")                    # IMPROVEMENT: Cleanup message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Receiver")  # IMPROVEMENT
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")  # IMPROVEMENT
    parser.add_argument("--output", type=str, default="received_file.jpg", help="Unused (per lab spec)")  # IMPROVEMENT
    args = parser.parse_args()                                # IMPROVEMENT: Parse arguments

    run_server(args.port, args.output)                        # IMPROVEMENT: Start server