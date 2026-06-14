import { FragmentDrawer } from './FragmentDrawer';
import { FragmentMain } from './FragmentMain';
import { FragmentPlayer } from './FragmentPlayer';
@Entry @Component
export struct MainActivity {
  @State isDrawerOpen: boolean = false
  @State isPlayerExpanded: boolean = false
  @State allowDrawerSwipe: boolean = true

  build() {
    SideBarContainer(SideBarContainerType.Embed) {
      // Drawer content (FragmentDrawer)
      FragmentDrawer()

      // Main content area
      Column() {
        // Main fragment (FragmentMain)
        FragmentMain()

        // Sliding panel (player area)
        Column() {
          // Player header (drag view)
          Row() {
            Text("PureMusic")
              .fontSize(16)
              .fontColor('#FFFFFF')
              .fontWeight(FontWeight.Bold)
            Blank()
            Button() {
              Image($r('app.media.ic_close_white'))
                .width(24)
                .height(24)
                .objectFit(ImageFit.Contain)
            }
            .width(40)
            .height(40)
            .backgroundColor('#00000000')
            .onClick(() => {
              this.isPlayerExpanded = false
            })
          }
          .width('100%')
          .height(56)
          .backgroundColor('#1A1A1A')
          .padding({ left: 16, right: 16 })

          // Player fragment (FragmentPlayer)
          if (this.isPlayerExpanded) {
            FragmentPlayer()
          }
        }
        .width('100%')
        .height(this.isPlayerExpanded ? '100%' : 56)
        .position({ y: '100%' })
        .translate({ y: this.isPlayerExpanded ? '-100%' : '-56px' })
        .gesture(
          PanGesture()
            .onActionStart((event: GestureEvent) => {})
            .onActionUpdate((event: GestureEvent) => {})
            .onActionEnd((event: GestureEvent) => {
              if (event.offsetY < -100) {
                this.isPlayerExpanded = true
              } else if (event.offsetY > 100) {
                this.isPlayerExpanded = false
              }
            })
        )
      }
      .width('100%')
      .height('100%')
    }
    .sideBarWidth(330)
    .showSideBar(this.isDrawerOpen)
    .onChange((value: boolean) => {
      this.isDrawerOpen = value
    })
  }
}