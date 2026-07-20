from typing import List
import argparse

polygon : List[tuple] = [                    
                    (
                        -35.3616073340025,
                        149.15937664539
                    ),
                    (
                        -35.36098612489909,
                        149.16093523704586
                    ),
                    (
                        -35.361616083523565,
                        149.16261184515514
                    ),
                    (
                        -35.36405935394708,
                        149.16266548934885
                    ),
                    (
                        -35.3648249228003,
                        149.16108544066583
                    ),
                    (
                        -35.36408560174981,
                        149.15933373006305
                    )
                ]

parser = argparse.ArgumentParser()

port : int = parser.add_argument("--port",
                                    type = int,
                                    default = 14550,
                                    help = "To specify the port for the connection",
                                    )
args = parser.parse_args()

port = args.port
                    
