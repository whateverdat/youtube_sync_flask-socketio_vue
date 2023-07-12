<script>
export default {
    data() {
        return {
            socket: null,
            videoElement: null,
            paused: null,
        };
    },
    created() {
        document.addEventListener('DOMContentLoaded', () => {
            this.videoElement = this.$refs.video;
            this.socket = io.connect('http://localhost:5000/');   // When created, connect to socket,
            this.socket.emit('join', { room: this.$route.path }); // then join room

            this.socket.on('pause', () => { // Pause without emitting to server a second time,
                this.pause(false);            // works like this: when any client emits pause or play,
            });                             // this code is activated for other clients,

            this.socket.on('play', () => {  // and because it has false parameter,
                this.play(false);             // it does not emit a second time, causing a loop.
            });

            this.socket.on('sync', (data) => { // Send current data to synchronize all clients
                this.videoElement.currentTime = data.time;
                if (data.state) { // If the state is playing, then also play the video
                    this.play(false);
                    return;
                }
                this.pause(false);
            });

            this.socket.on('user-joined', () => {
                // if (!this.videoElement) {
                //   this.delay(0.5);
                // }                           // When user joins, if video time is higher then 1,
                if (this.videoElement && this.videoElement.currentTime > 1) { // Other parties emit sync to the socket, to update
                    this.socket.emit('sync', { room: this.$route.path, time: this.videoElement.currentTime, state: this.pause, src: this.videoElement.src }); // joining user's video
                }
            });
        });
    },
    methods: {
        updatePaused(event) {               // State of the video
            this.videoElement = event.target; // Update videoElement as well
            this.paused = event.target.paused;
        },
        fullScreen() {
            if (this.videoElement.mozRequestFullScreen) {
                this.videoElement.mozRequestFullScreen();
            } else if (this.videoElement.webkitRequestFullScreen) {
                this.videoElement.webkitRequestFullScreen();
            }
        },
        play(emit) {               // Emit play with additional argument, to avoid
            this.videoElement.play(); // sending infinite emits between clients
            if (emit) {
                this.socket.emit('play', { room: this.$route.path });
                this.sync();
            }
        },
        pause(emit) { // Same as play
            this.videoElement.pause();
            if (emit) {
                this.socket.emit('pause', { room: this.$route.path });
                this.sync();
            }
        },
        sync() { // emit sync, send room information, time and video state
            console.log(this.$refs);
            this.socket.emit('sync', { room: this.$route.path, time: this.videoElement.currentTime, state: this.paused });
        },
        delay(time) {
            return new Promise(resolve => setTimeout(resolve, time));
        }
    },
    computed: {
        playing() {
            return !this.paused;
        },
    },
};
</script>
<template>
    <div class="flex flex-row justify-center h-screen m-auto bg-zinc-300 dark:bg-zinc-800">
        <div>
            <video class="w-2/3 m-auto mt-5 rounded-t" ref="video" autoplay="true" @canplay="updatePaused"
                @play="updatePaused" @pause="updatePaused" @timeupdate="$forceUpdate"
                src="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"></video>
            <div v-if="videoElement" class="controls flex w-2/3 m-auto rounded-b bg-zinc-400 p-0.5 dark:bg-zinc-700">
                <button class="mx-3" v-show="paused" @click="play(true)">&#9654;</button>
                <button class="mx-3" v-show="playing" @click="pause(true)">&#9208;</button>
                <input @change="sync" v-model="videoElement.currentTime" class="w-full" type="range" min="0"
                    :max="videoElement.duration" />
                <!-- A rather messy formatting, it basicly just adds 0 to beginning if seconds is smaller than 10, eg: 2:04 instead of 2:4  -->
                <h3 class="text-sm whitespace-nowrap mx-3">
                    {{ Math.floor(videoElement.currentTime / 60) + ':' + (Math.floor(videoElement.currentTime % 60 < 10)
                        ? '0' + Math.floor(videoElement.currentTime % 60) : Math.floor(videoElement.currentTime % 60)) }} /
                        {{ Math.floor(videoElement.duration / 60) + ':' + (Math.floor(videoElement.duration % 60 < 10) ? '0'
                            + Math.floor(videoElement.duration % 60) : Math.floor(videoElement.duration % 60)) }} </h3>
                        <input type="range" v-model="this.videoElement.volume" min="0" max="1" step="0.01">
                        <button class="mx-3" @click="fullScreen">&#x26F6;</button>
                        <!-- Make video volume, video full-screen -->
            </div>
        </div>
        <div class="flex justify-center">
            <input class="m-auto">
            <button class="button">GO</button>
        </div>
    </div>
</template>
