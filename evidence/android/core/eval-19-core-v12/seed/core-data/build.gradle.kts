plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "dev.skyl.notes.coredata"
    compileSdk = 36
    defaultConfig { minSdk = 26 }
}

dependencies {
    api("androidx.core:core-ktx:1.15.0")
    api("com.squareup.moshi:moshi:1.15.1")
    api("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
}
