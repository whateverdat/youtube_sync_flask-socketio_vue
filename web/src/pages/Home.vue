<script>
export default {
  data() {
    return {
      roomID: '',
    };
  },
  methods: {
    print() {
      console.log(this.roomID);
    }
  }
};
</script>

<template>
  <div class="flex justify-center h-screen bg-zinc-300 dark:bg-zinc-800">
    <div class="m-auto bg-black dark:bg-white dark:bg-opacity-5 bg-opacity-5 p-20 rounded shadow-lg">
      <div>
        <input class="p-1" v-model="roomID" placeholder="Enter Secret Key" type="text" />
        <router-link target="_blank" :to="roomID.toLowerCase()" class="button">Join</router-link>
      </div>
    </div>
  </div>
</template>
