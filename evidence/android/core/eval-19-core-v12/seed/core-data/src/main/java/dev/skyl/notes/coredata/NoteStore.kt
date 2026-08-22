package dev.skyl.notes.coredata

import java.io.File

data class Note(val id: String, val title: String, val body: String)

/**
 * Notes on local storage, one JSON file per note.
 *
 * Every method here touches the filesystem and returns when it is done. There is no
 * asynchronous variant.
 */
class NoteStore(private val directory: File) {

    /** Reads and parses every note file. A full library is a few thousand of them. */
    fun readAll(): List<Note> = emptyList()

    /** Writes [content] and returns when the bytes are on disk. */
    fun writeBackup(content: String) { /* ... */ }
}
