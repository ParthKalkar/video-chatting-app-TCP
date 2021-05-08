const redis = require("redis");
const client = redis.createClient();


//initiate call
export const make_call = (id) => {
    client.set("make_call","TRUE");
    client.set("correspondent_id",id)
}

// toggle video
export const video_on = () => {
    client.set("use_video","TRUE");
}

export const video_off = () => {
    client.set("use_video","FALSE");
}


// toggle audio
export const audio_on = () => {
    client.set("use_audio","TRUE");
}

export const audio_off = () => {
    client.set("use_audio","FALSE");
}

//submit a username
export const submit_username = (username) => {
    client.set("username",username);
}

//get the list of online people

//check if there is an incoming call

//check caller info

//accept an incoming call

//decline an incoming call