class MicProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.frameSamples = 960; // 20ms at 48kHz mono before stereo expansion
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0 || !input[0] || input[0].length === 0) {
      return true;
    }

    const mono = input[0];
    for (let i = 0; i < mono.length; i++) {
      this.buffer.push(mono[i]);
    }

    while (this.buffer.length >= this.frameSamples) {
      const pcm = new Int16Array(this.frameSamples * 2); // stereo interleaved
      for (let i = 0; i < this.frameSamples; i++) {
        const sample = Math.max(-1, Math.min(1, this.buffer[i]));
        const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        pcm[i * 2] = intSample;
        pcm[i * 2 + 1] = intSample;
      }
      this.buffer = this.buffer.slice(this.frameSamples);
      this.port.postMessage(pcm.buffer, [pcm.buffer]);
    }
    return true;
  }
}

registerProcessor('mic-processor', MicProcessor);
