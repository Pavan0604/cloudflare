const { S3Client } = require("@aws-sdk/client-s3");
const { MediaConvertClient, DescribeEndpointsCommand, CreateJobCommand, PresetListBy, ScalingBehavior, BillingTagsSource, ContainerType } = require("@aws-sdk/client-mediaconvert");

const region = process.env.AWS_REGION;
const roleArn = process.env.MEDIA_CONVERT_ROLE_ARN;
const queueArn = process.env.MEDIA_CONVERT_QUEUE_ARN;
const s3Bucket = process.env.INAPP_MEDIA_S3_BUCKET_NAME;

// Initialize AWS clients
const s3Client = new S3Client({ region });

// Extract filename without extension
function extractBaseName(path) {
    return path.split("/").reverse()[0].split(".")[0];
}

// Extract file extension
function extractFileExt(path) {
    return path.split("/").reverse()[0].split(".")[1];
}

// Get account ID from file path
function getAccount(path) {
    return path.split("/")[1];
}

exports.handler = async (event) => {
    console.log('Received event:', JSON.stringify(event, null, 2));
    var key = event.Records[0].s3.object.key;
    var fileExt = extractFileExt(key)
    //var outputPrefix = getAccount(key) + '/' + extractBaseName(key);
    var outputPrefix = 'dist/' + getAccount(key);
    console.log(`File: ${key}, Extension: ${fileExt}, "outputPrefix": ${outputPrefix}`);

    let jobSettings = null;

    console.log(`Processing file: ${key}, Extension: ${fileExt}`);

    if (fileExt === "mp4") {
        destKeyPath = outputPrefix + '/v/' + extractBaseName(key) + "/playlist";
        posterdestKeyPath = outputPrefix + '/v/' + extractBaseName(key);
        jobSettings = createMediaConvertJobSettings(key, destKeyPath, posterdestKeyPath);
    }
    if (fileExt === 'mp3' || fileExt === 'mpeg') {
        destKeyPath = outputPrefix + '/a/' + extractBaseName(key) + "/playlist";
        jobSettings = createAudioConvertJobSettings(key, destKeyPath);
    }


    if (jobSettings) {
        const mediaConvertClient = new MediaConvertClient({ region });
        const endpointCommand = new DescribeEndpointsCommand({});
        const endpoints = await mediaConvertClient.send(endpointCommand);
        const endpointUrl = endpoints.Endpoints[0].Url;

        // Create a new MediaConvert client with the endpoint
        const mediaConvert = new MediaConvertClient({ region, endpoint: endpointUrl });

        try {
            const jobCommand = new CreateJobCommand(jobSettings);
            const response = await mediaConvert.send(jobCommand);
            console.log(`MediaConvert job created: ${response.Job.Id}`);
        } catch (error) {
            console.error("Error creating MediaConvert job:", error);
            return { statusCode: 500, body: JSON.stringify(error) };
        }

        return { statusCode: 200, body: JSON.stringify("MediaConvert job submitted successfully!") };
    }
}

function createMediaConvertJobSettings(key, destKeyPath, posterdestKeyPath) {
    return {
        Queue: queueArn,
        Role: roleArn,
        Settings: {
            OutputGroups: [
                {
                    Name: "Apple HLS",
                    OutputGroupSettings: {
                        Type: "HLS_GROUP_SETTINGS",
                        HlsGroupSettings: {
                            SegmentControl: "SINGLE_FILE",
                            SegmentLength: 10,
                            Destination: "s3://" + s3Bucket + "/" + destKeyPath,
                            DestinationSettings: {
                                S3Settings: {
                                    StorageClass: "STANDARD"
                                }
                            },
                            MinSegmentLength: 0,
                        }
                    },
                    Outputs: [
                        {
                            NameModifier: "/2M",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            VideoDescription: {
                                Width: 1024,
                                ScalingBehavior: "FIT_NO_UPSCALE",
                                Height: 768,
                                CodecSettings: {
                                    Codec: "H_264",
                                    H264Settings: {
                                        NumberReferenceFrames: 3,
                                        GopSize: 90,
                                        HrdBufferSize: 16848,
                                        RateControlMode: "QVBR",
                                        MaxBitrate: 1872000,
                                        CodecProfile: "MAIN",
                                        CodecLevel: "LEVEL_3_1",
                                        GopSizeUnits: "FRAMES"
                                    }
                                }
                            }
                        },
                        {
                            NameModifier: "/15M",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            VideoDescription: {
                                Width: 960,
                                ScalingBehavior: "FIT_NO_UPSCALE",
                                Height: 640,
                                CodecSettings: {
                                    Codec: "H_264",
                                    H264Settings: {
                                        NumberReferenceFrames: 3,
                                        GopSize: 90,
                                        HrdBufferSize: 12348,
                                        RateControlMode: "QVBR",
                                        MaxBitrate: 1372000,
                                        CodecProfile: "MAIN",
                                        CodecLevel: "LEVEL_3_1",
                                        GopSizeUnits: "FRAMES"
                                    }
                                }
                            }
                        },
                        {
                            NameModifier: "/1M",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            VideoDescription: {
                                Width: 640,
                                ScalingBehavior: "FIT_NO_UPSCALE",
                                Height: 432,
                                CodecSettings: {
                                    Codec: "H_264",
                                    H264Settings: {
                                        NumberReferenceFrames: 3,
                                        GopSize: 90,
                                        HrdBufferSize: 7848,
                                        RateControlMode: "QVBR",
                                        MaxBitrate: 872000,
                                        CodecProfile: "MAIN",
                                        CodecLevel: "LEVEL_3",
                                        GopSizeUnits: "FRAMES"
                                    }
                                }
                            }
                        },
                        {
                            NameModifier: "/600k",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            VideoDescription: {
                                Width: 480,
                                ScalingBehavior: "FIT_NO_UPSCALE",
                                Height: 320,
                                CodecSettings: {
                                    Codec: "H_264",
                                    H264Settings: {
                                        NumberReferenceFrames: 3,
                                        GopSize: 90,
                                        HrdBufferSize: 4248,
                                        RateControlMode: "QVBR",
                                        MaxBitrate: 472000,
                                        EntropyEncoding: "CAVLC",
                                        CodecProfile: "BASELINE",
                                        CodecLevel: "LEVEL_3",
                                        GopSizeUnits: "FRAMES",
                                        NumberBFramesBetweenReferenceFrames: 0
                                    }
                                }
                            }
                        },
                        {
                            NameModifier: "/400k",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            VideoDescription: {
                                Width: 400,
                                ScalingBehavior: "FIT_NO_UPSCALE",
                                Height: 288,
                                CodecSettings: {
                                    Codec: "H_264",
                                    H264Settings: {
                                        NumberReferenceFrames: 1,
                                        GopSize: 90,
                                        HrdBufferSize: 2448,
                                        RateControlMode: "QVBR",
                                        MaxBitrate: 272000,
                                        EntropyEncoding: "CAVLC",
                                        CodecProfile: "BASELINE",
                                        CodecLevel: "LEVEL_3",
                                        GopSizeUnits: "FRAMES",
                                        NumberBFramesBetweenReferenceFrames: 0
                                    }
                                }
                            }
                        },
                        {
                            NameModifier: "/aud",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            AudioDescriptions: [
                                {
                                    AudioSourceName: "Audio Selector 1",
                                    CodecSettings: {
                                        Codec: "AAC",
                                        AacSettings: {
                                            Bitrate: 160000,
                                            CodecProfile: "LC",
                                            CodingMode: "CODING_MODE_2_0",
                                            SampleRate: 44100
                                        }
                                    }
                                }
                            ]
                        },
                    ]
                },
                {
                    Name: "File Group",
                    OutputGroupSettings: {
                        Type: "FILE_GROUP_SETTINGS",
                        FileGroupSettings: {
                            Destination: "s3://" + s3Bucket + "/" + posterdestKeyPath,
                        }
                    },
                    Outputs: [
                        {
                            NameModifier: "/poster",
                            ContainerSettings: {
                                Container: "RAW"
                            },
                            VideoDescription: {
                                Width: 960,
                                ScalingBehavior: "FILL",
                                Height: 540,
                                CodecSettings: {
                                    Codec: "FRAME_CAPTURE",
                                    FrameCaptureSettings: {
                                        FramerateNumerator: 1,
                                        FramerateDenominator: 300
                                    }
                                }
                            },
                        }
                    ]
                }
            ],
            FollowSource: 1,
            Inputs: [
                {
                    AudioSelectors: {
                        "Audio Selector 1": {
                            DefaultSelection: "DEFAULT"
                        }
                    },
                    FileInput: "s3://" + s3Bucket + "/" + key,
                }
            ]
        },
        BillingTagsSource: "JOB",
        AccelerationSettings: {
            Mode: "DISABLED"
        }
    }
}

function createAudioConvertJobSettings(key, destKeyPath){
    return {
        Queue: queueArn,
        Role: roleArn,
        Settings: {
            OutputGroups: [
                {
                    Name: "Apple HLS",
                    OutputGroupSettings: {
                        Type: "HLS_GROUP_SETTINGS",
                        HlsGroupSettings: {
                            SegmentControl: "SINGLE_FILE",
                            SegmentLength: 10,
                            Destination: "s3://" + s3Bucket + "/" + destKeyPath,
                            DestinationSettings: {
                                S3Settings: {
                                    StorageClass: "STANDARD"
                                }
                            },
                            MinSegmentLength: 0,
                        }
                    },
                    Outputs: [
                        {
                            NameModifier: "/64k",
                            ContainerSettings: {
                                Container: "M3U8"
                            },
                            AudioDescriptions: [
                                {
                                    AudioSourceName: "Audio Selector 1",
                                    CodecSettings: {
                                        Codec: "AAC",
                                        AacSettings: {
                                            Bitrate: 64000,
                                            CodecProfile: "LC",
                                            CodingMode: "CODING_MODE_2_0",
                                            SampleRate: 44100
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            Inputs: [
                {
                    AudioSelectors: {
                        "Audio Selector 1": {
                            DefaultSelection: "DEFAULT"
                        }
                    },
                    FileInput: "s3://" + s3Bucket + "/" + key,
                }
            ]
        }
    }
}
