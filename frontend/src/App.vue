<template>
  <div id="app">
    <div class="block has-text-centered">
      <div class="container">
        <img style="width:150px;" src="./assets/favicon.png">
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
  name: 'app',
  metaInfo: {
    title: 'Flaskregul', // set a title
    titleTemplate: '%s', // title is now "My Example App - Yay!"
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' }
    ],
    link: [
      { rel: 'favicon', href: './assets/favicon.png' }
    ],
    htmlAttrs: {
      lang: 'en',
      amp: undefined // "amp" has no value
    }
  }
}
</script>
