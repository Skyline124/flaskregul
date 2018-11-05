<template>
  <div id="app">
    <div class="block has-text-centered">
      <div class="container">
        <img style="width:150px;" src="./assets/logo.png">
      </div>
    </div>

    <div class="block">
      <div class="container">
        <router-view/>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  name: 'app'
}
</script>
