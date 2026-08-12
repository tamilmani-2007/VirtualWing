from typing import List
import argparse

polygon : List[tuple] = [                    
                    (
                        -35.3616961,
                        149.1636683
                    ),
                    (
                        -35.3631586,
                        149.1629256
                    ),
                    (
                       -35.3628376,
                        149.1618796
                    ),
                    (
                        -35.3639165,
                        149.1612895
                    ),
                    (
                        -35.3643334,
                        149.1623892
                    ),
                    (
                        -35.3659141,
                        149.1616435
                    ),
                    (
                        -35.3646629,
                        149.1582419
                    ),
                    (
                        -35.3632231,
                        149.1591190
                    ),
                    (
                        -35.3634807,
                        149.1600283
                    ),
                    (
                        -35.3625046,
                        149.1605835
                    ),
                    (
                        -35.3620953,
                        149.1597292
                    ),
                    (
                        -35.3606185,
                        149.1604199
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
                    
