"""Explicit local entry; serving a page does not authorize a memory run."""
import argparse
from tools._s2oe_local_player import load_binding,Player,serve


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--binding",required=True)
    parser.add_argument("--binding-sha256",required=True)
    parser.add_argument("--authorization")
    parser.add_argument("--authorization-sha256")
    parser.add_argument("--port",type=int,default=43823)
    args=parser.parse_args()
    if bool(args.authorization)!=bool(args.authorization_sha256):
        parser.error("Authorization path and digest must be supplied together")
    binding=load_binding(args.binding,args.binding_sha256)
    player=Player(binding,args.authorization,args.authorization_sha256)
    server=serve(player,args.port)
    print(f"http://127.0.0.1:{server.server_port}/",flush=True)
    try:
        server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:
        pass
    finally:
        player.stop(reason="SERVER_SHUTDOWN")
        server.server_close()


if __name__=="__main__":
    main()
