<script>
export default {
  data() {
    return {
      socket: null,
      videoElement: null,
      paused: null,
      chat: true,
      audio: false,
      targetURL: null,
      username: 'user-' + (Math.random() + 1).toString(36).substring(7),
      newUsername: null,
      message: null,
    };
  },
  created() {
    // const self = this;
    document.addEventListener('DOMContentLoaded', () => {
      this.newUsername = this.username;
      this.videoElement = this.$refs.video;
      this.socket = io.connect('http://localhost:5000/');   // When created, connect to socket,
      this.socket.emit('join', { room: this.$route.path }); // then join room

      // window.addEventListener('beforeunload', () => {
      //   const xhr = new XMLHttpRequest();
      //   xhr.open('POST', 'http://localhost:5000/client-close', false);  // Make the request synchronous
      //   xhr.setRequestHeader('Content-Type', 'application/json');
      //   xhr.send(JSON.stringify({ room: this.$route.path, user: this.username }));
      // });

      this.socket.on('pause', () => { // Pause without emitting to server a second time,
        this.pause(false);            // works like this: when any client emits pause or play,
      });                             // this code is activated for each client,

      this.socket.on('play', () => {  // and because it has false parameter,
        this.play(false);             // it does not emit a second time, causing a loop: see pause or play function below
      });

      this.socket.on('sync', (data) => { // Send current data to synchronize all clients
        if (data.source && data.source != this.videoElement.src) {
          this.videoElement.src = data.source;
        }
        this.videoElement.currentTime = data.time;
        if (data.state) {
          this.play(false);
          return;
        }
      });

      this.socket.on('sync-me', (data) => {
        if (data.user != this.username) {
          console.log('sync');
          this.sync();
        }
      });

      this.socket.on('user-joined', () => {
        if (this.videoElement && this.videoElement.currentTime > 1) { // Other parties emit sync to the socket, to update
          this.socket.emit('sync', {                                  // joining user's video
            room: this.$route.path,
            time: this.videoElement.currentTime,
            state: this.pause, source: this.videoElement.src
          });
        } else {
          this.sendMessage('has joined the room.');
        }
      });

      this.socket.on('client-close', (data) => {
        console.log(data);
      });

      this.socket.on('change-video', (data) => {
        if (data.source != 'error') {
          this.videoElement.src = data.source;
        }
      });

      this.socket.on('message', (data) => {
        this.$refs.chatBox.value += `${data.user} ${data.message}\n`;
        this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight;
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
        this.sendMessage('has played the video.');
      }
    },
    pause(emit) { // Same as play
      this.videoElement.pause();
      if (emit) {
        this.socket.emit('pause', { room: this.$route.path });
        this.sync();
        this.sendMessage('has paused the video.');
      }
    },
    sync() { // emit sync, send room information, time and video state
      this.socket.emit('sync', { room: this.$route.path, time: this.videoElement.currentTime, state: this.paused });
    },
    syncMe() {
      this.socket.emit('sync-me', { room: this.$route.path, user: this.username });
    },
    changeVideo(newURL) {
      // this.videoElement.src = newURL;
      this.socket.emit('change-video', { room: this.$route.path, source: newURL });
      this.sendMessage('is changing the video.');
    },
    sendMessage(message) {
      if (!message) {
        return;
      }
      if (this.newUsername && this.newUsername != this.username) {
        this.socket.emit('message', { room: this.$route.path, message: `has changed their username to ${this.newUsername}.`, user: this.username });
        this.username = this.newUsername;
        this.sendMessage(message);
      } else {
        this.socket.emit('message', { room: this.$route.path, message: message, user: this.username + ' ' });
        this.message = null;
      }
    },
    formatTime(time) {
      return Math.floor(time / 60) + ':' + (Math.floor(time % 60 < 10) ? '0' +
        Math.floor(time % 60) : Math.floor(time % 60));
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
  <!-- Page -->
  <div class="grid grid-cols-[20%_80%] justify-center h-screen m-auto bg-zinc-300 dark:bg-zinc-800">
    <!-- Chat section -->
    <div class="ml-10 flex flex-col">
      <!-- Hide/show chat button -->
      <button class="button" @click="chat = !chat" v-text="(chat ? 'Hide' : 'Show') + ' Chat'"></button>
      <!-- Username controls -->
      <div v-show="chat" class="flex justify-around">
        <h6 class="text-xs">Your username:</h6>
        <input v-model="newUsername" class="h-2/3 w-1/2" type="text">
      </div>
      <!-- Chat display -->
      <textarea ref="chatBox" v-show="chat" class="rounded-t p-2 resize-none text-xs" readonly cols="80"
        rows="30"></textarea>
      <!-- Chat interaction -->
      <input v-show="chat" @keyup.enter="sendMessage(message)" class="mt-1 rounded-none" v-model="message"
        @submit="sendMessage(message)" size="80" placeholder="Enter your message here">
    </div>
    <!-- Video section -->
    <div class="">
      <!-- Video source -->
      <video class="w-2/3 max-w-2/3 max-h-[500px] m-auto mt-5 rounded-t" autoplay="true" @canplay="updatePaused"
        @play="updatePaused" @pause="updatePaused" @timeupdate="$forceUpdate"
        src="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"></video>
      <!-- Video Controls -->
      <div v-if="videoElement"
        class="controls flex w-2/3 justify-center m-auto rounded-b bg-zinc-400 p-0.5 dark:bg-zinc-700">
        <!-- Play/pause button -->
        <button class="mx-3" v-show="paused" @click="play(true)">&#9654;</button>
        <button class="mx-3" v-show="playing" @click="pause(true)">&#9208;</button>
        <!-- Video time slider -->
        <input @change="sync(),
          sendMessage(`${username} has skipped to ${formatTime(videoElement.currentTime)}`)"
          v-model="videoElement.currentTime" class="w-full" type="range" min="0" :max="videoElement.duration" />
        <h3 class="text-sm whitespace-nowrap mx-3">
          {{ formatTime(videoElement.currentTime) }} / {{ formatTime(videoElement.duration) }} </h3>
        <!-- Audio control -->
        <button @click="audio = !audio">&#128266;</button>
        <!-- Mute -->
        <button v-show="audio" @click="videoElement.volume = 0">&#128263;</button>
        <!-- Audio slider -->
        <input v-show="audio" type="range" v-model="this.videoElement.volume" min="0" max="1" step="0.01">
        <!-- Fullscreen -->
        <button class="mx-3" @click="fullScreen">&#x26F6;</button>
      </div>
      <!-- Change video control -->
      <div v-if="videoElement" class="flex justify-around w-2/3 m-auto">
        <button class="button" @click="syncMe">Sync</button>
        <input class="m-auto w-full" v-model="targetURL" placeholder="Enter YouTube link">
        <button class="button" @click="changeVideo(targetURL)">Change</button>
      </div>
    </div>
  </div>
</template>

<style>
/* Make video controls disappear on fullscreen */
video::-webkit-media-controls {
  display: none !important;
}
</style>