
# This program was modified by Davinder Kehal / N01718686

import socket
import argparse
import struct  # IMPROVEMENT: Handle sequence numbers

def run_server(port, output_file):
    # 1. Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Bind the socket to the port (0.0.0.0 means all interfaces)
    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    print(f"[*] Server will save each received file as 'received_<ip>_<port>.jpg' based on sender.")
    sock.bind(server_address)

    # 3. Keep listening for new transfers
    try:
        while True:
            f = None
            expected_seq = 0      # IMPROVEMENT: Track expected packet
            buffer = {}           # IMPROVEMENT: Store out-of-order data
            sender_filename = None
            reception_started = False
            while True:
                data, addr = sock.recvfrom(4096)
                seq_num = struct.unpack("!I", data[:4])[0]  # IMPROVEMENT: Read sequence number
                payload = data[4:]                          # IMPROVEMENT: Extract payload
                # Protocol: If we receive an empty packet, it means "End of File"
                if not payload:#IMPROVEMENT::this is required because of the header
                    print(f"[*] End of file signal received from {addr}. Closing.")
                    break
                if f is None:
                    print("==== Start of reception ====")
                    ip, sender_port = addr
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, 'wb')
                    print(f"[*] First packet received from {addr}. File opened for writing as '{sender_filename}'.")
                # Write data to disk
                if seq_num == expected_seq:
                    f.write(payload)                      # IMPROVEMENT: Write in-order data
                    expected_seq += 1                     # IMPROVEMENT: Move to next sequence
                    while expected_seq in buffer:
                        f.write(buffer.pop(expected_seq)) # IMPROVEMENT: Flush buffered data
                        expected_seq += 1                 # IMPROVEMENT: Advance sequence
                elif seq_num > expected_seq:
                    buffer[seq_num] = payload             # IMPROVEMENT: Buffer out-of-order data
                else:
                    pass                                  # IMPROVEMENT: Ignore duplicate packet
                sock.sendto(struct.pack("!I", seq_num), addr)  # IMPROVEMENT: Send ACK back to client# Send ACK back to sender
                                                                
                # print(f"Server received {len(data)} bytes from {addr}") # Optional: noisy
            if f:
                f.close()
            print("==== End of reception ====")
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data")
    args = parser.parse_args()

    try:
        run_server(args.port, args.output)
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")