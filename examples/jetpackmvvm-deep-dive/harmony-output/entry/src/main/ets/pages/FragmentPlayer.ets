import { router } from '@kit.ArkUI';

interface PlayerState {
  musicId: string;
  title: string;
  artist: string;
  coverImg: string;
  maxSeekDuration: number;
  currentSeekPosition: number;
  isPlaying: boolean;
  playModeIcon: string;
  placeHolder: string;
  repeatMode: string;
}

interface SlideAnimatorStates {
  albumArtSize: number;
  customToolbarVisibility: boolean;
  songProgressNormalVisibility: boolean;
  summaryTranslationY: number;
  titleTranslationX: number;
  artistTranslationX: number;
  artistTranslationY: number;
  iconContainerY: number;
  nextX: number;
  playPauseX: number;
  playCircleAlpha: number;
  playPauseDrawableColor: string;
  previousAlpha: number;
  previousVisibility: boolean;
  previousX: number;
  modeAlpha: number;
  modeVisibility: boolean;
  modeX: number;
  icPlayListX: number;
}

@Entry
@Component
export struct FragmentPlayer {
  @State playerState: PlayerState = {
    musicId: '',
    title: 'PureMusic',
    artist: 'KunMinX',
    coverImg: '',
    maxSeekDuration: 100,
    currentSeekPosition: 30,
    isPlaying: false,
    playModeIcon: 'repeat',
    placeHolder: 'bg_album_default',
    repeatMode: 'LIST_CYCLE'
  };

  @State slideAnimatorStates: SlideAnimatorStates = {
    albumArtSize: 200,
    customToolbarVisibility: false,
    songProgressNormalVisibility: false,
    summaryTranslationY: 0,
    titleTranslationX: 0,
    artistTranslationX: 0,
    artistTranslationY: 0,
    iconContainerY: 250,
    nextX: 0,
    playPauseX: 40,
    playCircleAlpha: 1,
    playPauseDrawableColor: '#000000',
    previousAlpha: 1,
    previousVisibility: true,
    previousX: 80,
    modeAlpha: 1,
    modeVisibility: true,
    modeX: 120,
    icPlayListX: -40
  };

  @State seekPosition: number = 30;
  @State isSeeking: boolean = false;

  build() {
    Stack({ alignContent: Alignment.Top }) {
      // Album art background
      Image($r('app.media.bg_album_default'))
        .width(this.slideAnimatorStates.albumArtSize)
        .height(this.slideAnimatorStates.albumArtSize)
        .objectFit(ImageFit.Cover)
        .margin({ top: 0 })
        .position({ x: 0, y: 0 })
        .zIndex(0)

      // Custom toolbar at top
      if (!this.slideAnimatorStates.customToolbarVisibility) {
        Row() {
          Button() {
            Image($r('app.media.ic_close_white'))
              .width(28)
              .height(28)
              .objectFit(ImageFit.Contain)
          }
          .width(36)
          .height(36)
          .backgroundColor('transparent')
          .onClick(() => {
            // TODO: slideDown action
            this.slideAnimatorStates.customToolbarVisibility = true;
          })

          Blank()

          Button() {
            Text('...')
              .fontColor(Color.White)
              .fontSize(20)
          }
          .width(36)
          .height(36)
          .backgroundColor('transparent')
          .onClick(() => {
            // TODO: more action
          })
        }
        .width('100%')
        .height(56)
        .padding({ left: 16, right: 16 })
        .alignItems(VerticalAlign.Center)
        .position({ x: 0, y: 37 })
        .zIndex(10)
      }

      // Summary section
      Column() {
        // Song progress (normal)
        if (!this.slideAnimatorStates.songProgressNormalVisibility) {
          Progress({ value: this.playerState.currentSeekPosition, total: this.playerState.maxSeekDuration, type: ProgressType.Linear })
            .width('100%')
            .height(4)
            .margin({ bottom: 8 })
        }

        // Title
        Text(this.playerState.title)
          .fontSize(16)
          .fontColor(Color.Black)
          .maxLines(1)
          .constraintSize({ maxWidth: 200 })
          .translate({ x: this.slideAnimatorStates.titleTranslationX })
          .margin({ left: 12, right: 42 })

        // Artist
        Text(this.playerState.artist)
          .fontSize(14)
          .fontColor('#999999')
          .maxLines(1)
          .constraintSize({ maxWidth: 200 })
          .translate({
            x: this.slideAnimatorStates.artistTranslationX,
            y: this.slideAnimatorStates.artistTranslationY
          })
          .margin({ left: 12 })
      }
      .width('100%')
      .height(this.slideAnimatorStates.albumArtSize)
      .margin({ left: this.slideAnimatorStates.albumArtSize })
      .padding({ top: 20 })
      .justifyContent(FlexAlign.Start)
      .translate({ y: this.slideAnimatorStates.summaryTranslationY })
      .position({ x: 0, y: 0 })
      .zIndex(5)

      // Icon container
      Row() {
        // Mode button
        Button() {
          Text('↻')
            .fontColor(Color.Black)
            .fontSize(28)
        }
        .width(36)
        .height(36)
        .backgroundColor('transparent')
        .opacity(this.slideAnimatorStates.modeAlpha)
        .visibility(this.slideAnimatorStates.modeVisibility ? Visibility.Visible : Visibility.None)
        .translate({ x: this.slideAnimatorStates.modeX })
        .onClick(() => {
          // TODO: playMode action
          if (this.playerState.repeatMode === 'LIST_CYCLE') {
            this.playerState.repeatMode = 'SINGLE_CYCLE';
          } else if (this.playerState.repeatMode === 'SINGLE_CYCLE') {
            this.playerState.repeatMode = 'RANDOM';
          } else {
            this.playerState.repeatMode = 'LIST_CYCLE';
          }
        })

        // Previous button
        Button() {
          Image($r('app.media.ic_previous_dark'))
            .width(28)
            .height(28)
            .objectFit(ImageFit.Contain)
        }
        .width(36)
        .height(36)
        .backgroundColor('transparent')
        .opacity(this.slideAnimatorStates.previousAlpha)
        .visibility(this.slideAnimatorStates.previousVisibility ? Visibility.Visible : Visibility.None)
        .translate({ x: this.slideAnimatorStates.previousX })
        .onClick(() => {
          // TODO: previous action
          this.playerState.currentSeekPosition = 0;
        })

        // Play/Pause button
        Button() {
          Image(this.playerState.isPlaying ? $r('app.media.ic_action_pause') : $r('app.media.ic_action_play'))
            .width(28)
            .height(28)
            .objectFit(ImageFit.Contain)
        }
        .width(36)
        .height(36)
        .backgroundColor('transparent')
        .translate({ x: this.slideAnimatorStates.playPauseX })
        .onClick(() => {
          this.playerState.isPlaying = !this.playerState.isPlaying;
        })

        // Next button
        Button() {
          Image($r('app.media.ic_next_dark'))
            .width(28)
            .height(28)
            .objectFit(ImageFit.Contain)
        }
        .width(36)
        .height(36)
        .backgroundColor('transparent')
        .translate({ x: this.slideAnimatorStates.nextX })
        .onClick(() => {
          // TODO: next action
          this.playerState.currentSeekPosition = 0;
        })

        // Playlist button
        Button() {
          Text('≡')
            .fontColor(Color.Black)
            .fontSize(28)
        }
        .width(36)
        .height(36)
        .backgroundColor('transparent')
        .translate({ x: this.slideAnimatorStates.icPlayListX })
        .onClick(() => {
          // TODO: showPlayList action
        })
      }
      .width('100%')
      .height(36)
      .justifyContent(FlexAlign.End)
      .position({ x: 0, y: this.slideAnimatorStates.iconContainerY })
      .zIndex(6)

      // Seekbar at bottom
      Slider({
        value: this.seekPosition,
        min: 0,
        max: this.playerState.maxSeekDuration,
        step: 1,
        style: SliderStyle.OutSet
      })
        .width('100%')
        .height(6)
        .blockColor('#666666')
        .trackColor('#CCCCCC')
        .selectedColor('#FF6E40')
        .padding({ top: 24 })
        .position({ x: 0, y: 'calc(100% - 30)' })
        .zIndex(7)
        .onChange((value: number) => {
          this.seekPosition = value;
          this.playerState.currentSeekPosition = value;
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor(Color.White)
  }
}