
<template>

  <div class="block">
      <div class="column is-fullwidth has-text-centered">
        <div class="button has-text-weight-bold is-large is-fullwidth"
        v-bind:class="{
          'is-info': (temperature <= 18),
          'is-primary': (18 < temperature && temperature <= 21),
          'is-warning': (21 < temperature && temperature <= 23),
          'is-danger': (temperature > 23),
          'is-loading': (temperature === '??')
        }"
        @click="getTemperature">
          {{ temperature }} °C
          
          <span v-if="(temperature > 21)">&nbsp;</span>
          <font-awesome-icon v-if="(temperature > 21)" icon="chevron-circle-up"/>

          <span v-if="(temperature < 20)">&nbsp;</span>
          <font-awesome-icon v-if="(temperature < 20)" icon="chevron-circle-down" />
        </div>
      </div>

    <div class="block">
          <div class="column is-fullwidth has-text-centered">
            <button class="button is-primary is-large"
            v-bind:class="{
              'is-outlined': (regulation === 'manual'),
              'is-loading': (regulation === 'wait')
            }"
            id="regul-btn"
            v-on:click="toggleRegulation( 'auto' )">
                Auto
            </button>
            <button class="button is-large is-danger"
            v-bind:class="{
              'is-outlined': (regulation === 'auto'),
              'is-loading': (regulation === 'wait')
            }"
            id="manual-btn"
            v-on:click="toggleRegulation( 'manual' )">
                Manual
            </button>
          </div>

          <div class="block">
            <div class="notification"
           style="margin-left: 12px; margin-right: 12px">Regulation = {{ regulation }}</div>
          </div>
    </div>
    
    <div class="block"
    style="margin-left: 12px; margin-right: 12px"> 
      <span> Manual regulation value </span>
      <div class="notification"
      v-bind:class="{
        'is-danger': (regulation === 'wait' || waitingForValue === 'wait')
      }"
      style='margin-bottom: 50px'
      >
        <vue-slider
          ref="slider"
          tooltip-dir="bottom"
          v-model="sliderValue"
          @drag-end="sliderDragEnd"
          style="margin-left: 20px; margin-right: 20px;"
          :disabled="(regulation !== 'manual')"
        ></vue-slider>
      </div>
    </div>

  </div>

</template>


<script>
import axios from 'axios'
import vueSlider from 'vue-slider-component'
export default {
  data () {
    return {
      randomNumber: 0,
      regulation: 'auto',
      waitingForValue: 'no',
      circleSliderValue: 0,
      sliderValue: 0,
      temperature: 20
    }
  },
  methods: {
    getRandomInt (min, max) {
      min = Math.ceil(min)
      max = Math.floor(max)
      return Math.floor(Math.random() * (max - min + 1)) + min
    },
    getRandom () {
      // this.randomNumber = this.getRandomInt(1, 100)
      this.randomNumber = this.getRandomFromBackend()
    },
    getRandomFromBackend () {
      const path = `http://192.168.1.67/api/random`
      axios.get(path)
      .then(response => {
        this.randomNumber = response.data.randomNumber
      })
      .catch(error => {
        console.log(error)
      })
    },
    getTemperature () {
      this.temperature = '??'
      console.log('waiting for temperature...')
      const path = `http://192.168.1.67/api/gettemperature`
      axios.get(path)
      .then(response => {
        this.temperature = response.data.temperature.toFixed(1)
      })
      .catch(error => {
        console.log(error)
      })
    },
    toggleRegulation (regul) {
      this.regulation = 'wait'
      const path = `http://192.168.1.67/api/setregulation`
      axios.post(path, {regulation: regul})
      .then(response => {
        console.log('Server regulation status = ' + response.data.realized)
        this.regulation = response.data.realized
      })
      .catch(error => {
        console.log(error.response.data.error)
        this.regulation = 'auto'
      })
    },
    /* End of dragging manual slider: demand
     * an update of the motor commanded position */
    sliderDragEnd (obj) {
      console.log('Client Demanded Value = ' + obj.getValue() + ' %')
      this.waitingForValue = 'wait'
      const path = `http://192.168.1.67/api/manualdemand`
      axios.post(path, {demanded: obj.getValue()})
      .then(response => {
        console.log('Server Realized Value = ' + response.data.realized + ' %')
        obj.setValue(response.data.realized)
        this.waitingForValue = 'no'
      })
      .catch(error => {
        console.log(error)
      })
    }
  },
  created () {
    this.getRandom()
  },
  components: {
    vueSlider
  }
}
</script>
