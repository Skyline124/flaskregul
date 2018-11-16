import Vue from 'vue'
import VueCircleSlider from 'vue-circle-slider'
import vueSlider from 'vue-slider-component'
import App from './App'
import router from './router'

import { faCoffee,
  faChevronCircleUp,
  faChevronCircleDown} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import Meta from 'vue-meta'

// Require the main Sass manifest file
require('./assets/sass/main.scss')

library.add(
  faCoffee,
  faChevronCircleUp,
  faChevronCircleDown)
Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.config.productionTip = false
Vue.use(VueCircleSlider, { globalComponent: true })
Vue.use(vueSlider, { globalComponent: true })
Vue.use(FontAwesomeIcon, { globalComponent: true })

Vue.use(Meta)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  render: h => h(App)
})
