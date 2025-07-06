<template>
  <div>
    <router-view>aéeeee</router-view>
  </div>
</template>

<script>
import { mapMutations } from 'vuex'

export default {
  data () {
    return {}
  },
  created () {
    this.setModule('routeCPF')
  },
  methods: {
    ...mapMutations('app', ['setModule']),
  },
}

</script>
