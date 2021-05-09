const redis = require("redis");
const client = redis.createClient();

exports.client = client;

//initiate call
exports.make_call = (id) => {
    client.set("make_call","TRUE");
    client.set("correspondent_id",id);
}

// toggle video
exports.video_on = () => {
    client.set("use_video","TRUE");
}

exports.video_off = () => {
    client.set("use_video","FALSE");
}


// toggle audio
exports.audio_on = () => {
    client.set("use_audio","TRUE");
}

exports.audio_off = () => {
    client.set("use_audio","FALSE");
}

//submit a username
exports.submit_username = (username) => {
    client.set("username",username);
    console.log("Username in JS : " + username);
}

//get the list of online people
exports.get_online = () => {
    var res = client.get("online_list", (err,val)=> {
        console.log(val);
        return JSON.parse(val);
    });
    
}

//check if there is an incoming call
exports.incoming_call = () => {
    return client.get("incoming_call", (err,val)=>val) == "TRUE";
}

exports.quit = () => {
    client.set("status","quit");
    console.log('changed status to quit!')
}

//check caller info

//accept an incoming call

//decline an incoming call